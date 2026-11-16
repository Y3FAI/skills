#!/usr/bin/env bash
# Drives the real Android phone over adb. Never an emulator.
# Copy to <project>/e2e/phone/scripts/android.sh; settings come from e2e/phone/phone.env.
#
#   android.sh build           Release build with the JS inside (pointed at the test server when
#                              API_PORT is set), installed and opened
#   android.sh launch          open the app          android.sh restart   force-stop, then open
#   android.sh shot <name>     screenshot to e2e/phone/.out/android/<name>.png
#   android.sh rec <name> <s>  screen recording (max 180 s) to .out/android/<name>.mp4
#   android.sh ids             every testID on screen, with its label and bounds
#   android.sh tap <id>        tap the element with that testID (waits up to 10 s for it)
#   android.sh type <text>     type into the focused field (ASCII only: digits, codes)
#   android.sh trail           the app's diagnostics trail (test builds only)
#   android.sh log [s]         logcat of the app's OWN process only, for s seconds (default 10)
#   android.sh notif           the app's own notifications: channel, importance, style
#   android.sh front           is the app in front? (exit 1 if not)
#   android.sh awake           keep the screen on for 10 min while testing; prints the old value
#
# The phone: ANDROID_SERIAL, or the only device `adb devices` lists.
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"   # e2e/phone
ROOT="$(cd "$HERE/../.." && pwd)"
OUT="$HERE/.out/android"
mkdir -p "$OUT"
# shellcheck disable=SC1091
[ -f "$HERE/phone.env" ] && . "$HERE/phone.env"
PKG="${APP_ANDROID_PACKAGE:-${APP_BUNDLE_ID:?set APP_BUNDLE_ID or APP_ANDROID_PACKAGE in phone.env}}"
MOBILE_DIR="$ROOT/${MOBILE_DIR:-apps/mobile}"
API_URL_VAR="${API_URL_VAR:-EXPO_PUBLIC_API_URL}"

export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
export PATH="$ANDROID_HOME/platform-tools:$PATH"

serial() {
  if [ -n "${ANDROID_SERIAL:-}" ]; then echo "$ANDROID_SERIAL"; return; fi
  local list
  list=$(adb devices | awk 'NR > 1 && $2 == "device" { print $1 }')
  [ -n "$list" ] || { echo "android: no phone (plug it in, USB debugging on, allow this Mac)" >&2; exit 1; }
  [ "$(echo "$list" | wc -l | tr -d ' ')" = 1 ] || { echo "android: several devices; set ANDROID_SERIAL" >&2; exit 1; }
  echo "$list"
}

# The screen's accessibility tree: testID is resource-id, the label is content-desc.
dump() {
  adb -s "$S" shell uiautomator dump /sdcard/phone-ui.xml >/dev/null 2>&1
  adb -s "$S" exec-out cat /sdcard/phone-ui.xml
}

# Taps are coordinates: when another app (a launcher, the clock) is in front they land there.
front() { adb -s "$S" shell dumpsys window 2>/dev/null | grep -E "mCurrentFocus|mFocusedApp" | grep -q "$PKG"; }

S=$(serial)
cmd="${1:-}"
shift || true
case "$cmd" in
  build)
    envs=""
    if [ -n "${API_PORT:-}" ]; then
      envs="$API_URL_VAR=http://${PHONE_LAN_IP:-$(ipconfig getifaddr en0)}:$API_PORT${API_PATH:-}"
    fi
    echo "android: Release build${envs:+, $envs}" >&2
    (
      cd "$MOBILE_DIR"
      # Gradle wants JDK 17; a newer default JDK breaks the build.
      JAVA_HOME="${JAVA_HOME_17:-$(/usr/libexec/java_home -v 17)}"
      export JAVA_HOME
      # android/ is generated: regenerate each build, so the app config (an http test server
      # needs cleartext allowed for it) is always the one built.
      env $envs npx expo prebuild -p android --no-install >"$OUT/prebuild.log" 2>&1
      env $envs EXPO_PUBLIC_DIAG=1 CI=1 npx expo run:android --variant release \
        --device "$S" --no-bundler >"$OUT/build.log" 2>&1
    ) || {
      grep -E "error|FAILURE|What went wrong" -A3 "$OUT/build.log" | tail -20 >&2
      echo "android: build failed ($OUT/build.log)" >&2
      exit 1
    }
    echo "android: installed" >&2
    ;;
  launch)
    adb -s "$S" shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
    echo launched
    ;;
  restart)
    adb -s "$S" shell am force-stop "$PKG"
    adb -s "$S" shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
    echo restarted
    ;;
  shot)
    f="$OUT/${1:-now}.png"
    adb -s "$S" exec-out screencap -p >"$f"
    echo "$f"
    ;;
  rec)
    name="${1:?name}"; secs="${2:-20}"
    [ "$secs" -le 180 ] || { echo "android: screenrecord stops at 180 s" >&2; exit 2; }
    # --bugreport: the phone's own time on every frame, and a frame only when the screen
    # changes, so frame gaps (framegaps.mjs) are real. Start it, then make the move.
    adb -s "$S" shell screenrecord --bugreport --bit-rate 4000000 --time-limit "$secs" "/sdcard/$name.mp4"
    adb -s "$S" pull "/sdcard/$name.mp4" "$OUT/$name.mp4" >/dev/null
    adb -s "$S" shell rm "/sdcard/$name.mp4"
    echo "$OUT/$name.mp4"
    ;;
  trail)
    dump | node -e '
      let x = require("fs").readFileSync(0, "utf8");
      const m = /resource-id="diag"[^>]*?content-desc="([^"]*)"|content-desc="([^"]*)"[^>]*?resource-id="diag"/.exec(x);
      if (!m) { console.log("(no trail: not a test build, or the app is not on screen)"); process.exit(0); }
      console.log((m[1] ?? m[2]).replace(/&#10;/g, "\n").replace(/&quot;/g, "\"").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">"));
    '
    ;;
  ids)
    dump | node -e '
      const x = require("fs").readFileSync(0, "utf8");
      for (const n of x.match(/<node [^>]*>/g) ?? []) {
        const id = /resource-id="([^"]*)"/.exec(n)?.[1];
        if (!id || id === "diag" || id.includes(":id/")) continue;
        const label = /content-desc="([^"]*)"/.exec(n)?.[1] || /text="([^"]*)"/.exec(n)?.[1] || "";
        console.log(`${id}  ${label.slice(0, 60)}  ${/bounds="([^"]*)"/.exec(n)?.[1]}`);
      }
    '
    ;;
  tap)
    id="${1:?testID}"
    front || { echo "FAIL tap:$id (the app is not in front)" >&2; exit 1; }
    for _ in $(seq 1 20); do
      at=$(dump | node -e '
        const x = require("fs").readFileSync(0, "utf8"), id = process.argv[1];
        for (const n of x.match(/<node [^>]*>/g) ?? []) {
          if (!n.includes(`resource-id="${id}"`)) continue;
          const [, a, b, c, d] = /bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"/.exec(n).map(Number);
          console.log(`${(a + c) >> 1} ${(b + d) >> 1}`); break;
        }' "$id")
      if [ -n "$at" ]; then adb -s "$S" shell input tap $at; echo "OK tap:$id"; exit 0; fi
      sleep 0.5
    done
    echo "FAIL tap:$id (not found)" >&2; exit 1
    ;;
  type)
    adb -s "$S" shell input text "${1:?text}"
    echo "OK type"
    ;;
  log)
    pid=$(adb -s "$S" shell pidof "$PKG" | tr -d '\r')
    [ -n "$pid" ] || { echo "android: the app is not running" >&2; exit 1; }
    adb -s "$S" logcat --pid="$pid" -v time -T 1 &
    LOG=$!; sleep "${1:-10}"; kill $LOG 2>/dev/null || true
    ;;
  notif)
    adb -s "$S" shell dumpsys notification --noredact | node -e '
      const text = require("fs").readFileSync(0, "utf8");
      // Only this app'"'"'s records are read; other apps'"'"' notifications are skipped.
      const heads = [...text.matchAll(/NotificationRecord\(0x[0-9a-f]+: pkg=([\w.]+) /g)];
      const records = heads.map((m, i) => [m[1], text.slice(m.index, heads[i + 1]?.index ?? m.index + 4000)])
        .filter(([pkg]) => pkg === process.argv[1]).map(([, r]) => r);
      if (!records.length) console.log("(no notification from the app)");
      for (const r of records) {
        const get = (re) => re.exec(r)?.[1] ?? "?";
        console.log(`channel=${get(/channel=([\w.]+)/)} importance=${get(/importance=(\d+)/)} ` +
          `style=${get(/android\.template=\S*?\.(\w+Style)/)} fullScreen=${/fullScreenIntent=PendingIntent/.test(r)}`);
      }
    ' "$PKG"
    ;;
  front) if front; then echo "front: $PKG"; else echo "front: not $PKG" >&2; exit 1; fi ;;
  awake)
    old=$(adb -s "$S" shell settings get system screen_off_timeout | tr -d '\r')
    adb -s "$S" shell settings put system screen_off_timeout 600000
    echo "screen stays on 10 min (was $old ms; restore: adb shell settings put system screen_off_timeout $old)"
    ;;
  *) echo "usage: android.sh build|launch|restart|shot|rec|ids|tap|type|trail|log|notif|front|awake" >&2; exit 2 ;;
esac
