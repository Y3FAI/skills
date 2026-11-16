#!/usr/bin/env bash
# Drives the real iPhone from the terminal. Never a simulator.
# Copy to <project>/e2e/phone/scripts/phone.sh; settings come from e2e/phone/phone.env.
#
#   phone.sh build                 Release build with the JS inside (pointed at the test server
#                                  when API_PORT is set), permission texts checked, installed
#   phone.sh runner                build the runner once, and after Steps.swift changes
#   phone.sh test                  every journey in e2e/phone/journeys, in ONE runner session
#   phone.sh test add history      only those journeys
#   phone.sh steps 'tap:home-add|expect:add-sheet|shot:add'   ad-hoc steps
#   phone.sh shot <name>           a screenshot of the phone as it is now
#   phone.sh launch                (re)start the app
#   phone.sh link <path> [s]       open a screen by deep link (APP_SCHEME://<path>), wait s
#
# Output: e2e/phone/.out/runs/<time>/: <journey>/NN-<shot>.png, recording.mp4 (XCTest's screen
# recording of the whole run), steps.log (every step with its time, and the app's DIAG trail).
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"   # e2e/phone
ROOT="$(cd "$HERE/../.." && pwd)"
OUT="$HERE/.out"
RUNNER="$OUT/runner"
mkdir -p "$OUT"
# shellcheck disable=SC1091
[ -f "$HERE/phone.env" ] && . "$HERE/phone.env"
: "${APP_BUNDLE_ID:?set APP_BUNDLE_ID in e2e/phone/phone.env}"
MOBILE_DIR="$ROOT/${MOBILE_DIR:-apps/mobile}"
API_URL_VAR="${API_URL_VAR:-EXPO_PUBLIC_API_URL}"

phone_udid() {
  if [ -n "${PHONE_UDID:-}" ]; then echo "$PHONE_UDID"; return; fi
  local json="$OUT/devices.json"
  xcrun devicectl list devices --json-output "$json" >/dev/null 2>&1 || true
  node -e '
    const r = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8")).result.devices;
    const p = r.find((d) => d.hardwareProperties?.platform === "iOS" &&
      d.hardwareProperties?.reality === "physical" && d.connectionProperties?.tunnelState !== "unavailable");
    console.log(p ? p.hardwareProperties.udid : "");
  ' "$json" 2>/dev/null
}

need_phone() {
  UDID=$(phone_udid)
  [ -n "$UDID" ] || { echo "phone: no iPhone connected (cable or Wi-Fi, unlocked, trusted)" >&2; exit 1; }
}

locked() {
  xcrun devicectl device info lockState --device "$UDID" --json-output "$OUT/lock.json" >/dev/null 2>&1 || return 1
  node -e 'process.exit(JSON.parse(require("fs").readFileSync(process.argv[1], "utf8")).result.passcodeRequired ? 0 : 1)' "$OUT/lock.json"
}

# XCUITest cannot drive a locked phone, and nobody but the owner types its passcode: wait.
need_unlocked() {
  locked || return 0
  local wait="${UNLOCK_WAIT:-120}" t=0
  echo "phone: the iPhone is locked; unlock it (waiting up to ${wait}s)" >&2
  while locked; do
    [ "$t" -ge "$wait" ] && { echo "phone: still locked; nothing ran" >&2; exit 1; }
    sleep 2; t=$((t + 2))
  done
  echo "phone: unlocked after ${t}s" >&2
}

api_env() {
  [ -n "${API_PORT:-}" ] || return 0
  local lan="${PHONE_LAN_IP:-$(ipconfig getifaddr en0)}"
  echo "$API_URL_VAR=http://$lan:$API_PORT${API_PATH:-}"
}

build_app() {
  need_phone
  : "${APP_NAME:?set APP_NAME (the Xcode product name, as in ios/<APP_NAME>/) in phone.env}"
  local envs
  envs=$(api_env)
  echo "phone: Release build for the iPhone${envs:+, $envs}" >&2
  (
    cd "$MOBILE_DIR"
    # ios/ is generated (and usually gitignored): regenerate it when it is missing or older
    # than the app config, else keep it so only what changed rebuilds.
    if [ ! -f "ios/$APP_NAME/Info.plist" ] || ! "$HERE/scripts/check-plist.sh" "ios/$APP_NAME/Info.plist" 2>/dev/null; then
      echo "phone: regenerating the native project (app config changed)" >&2
      env $envs npx expo prebuild -p ios --no-install >"$OUT/prebuild.log" 2>&1
    fi
    # EXPO_PUBLIC_DIAG=1: the app keeps its trail for the runner (diag.ts).
    env $envs EXPO_PUBLIC_DIAG=1 CI=1 npx expo run:ios --configuration Release \
      --device "$UDID" --no-bundler >"$OUT/build-ios.log" 2>&1
  ) || {
    # Built and installed; only the launch needs an unlocked phone.
    if grep -q "because the device is locked" "$OUT/build-ios.log"; then
      echo "phone: installed; the iPhone is locked, so it did not open" >&2
    else
      grep -E "error|Error" "$OUT/build-ios.log" | tail -15 >&2
      echo "phone: build failed ($OUT/build-ios.log)" >&2
      exit 1
    fi
  }
  local app
  app=$(ls -td "$HOME"/Library/Developer/Xcode/DerivedData/"$APP_NAME"-*/Build/Products/Release-iphoneos/"$APP_NAME".app | head -1)
  "$HERE/scripts/check-plist.sh" "$app"
  echo "phone: installed" >&2
}

build_runner() {
  need_phone
  : "${PHONE_TEAM_ID:?set PHONE_TEAM_ID (your Apple team id) in phone.env or the environment}"
  export PHONE_TEAM_ID PHONE_RUNNER_BUNDLE_PREFIX="${PHONE_RUNNER_BUNDLE_PREFIX:-$APP_BUNDLE_ID.phonerunner}"
  mkdir -p "$RUNNER"
  (cd "$HERE/runner" && xcodegen generate --spec project.yml --project "$RUNNER" --quiet)
  xcodebuild build-for-testing -project "$RUNNER/PhoneRunner.xcodeproj" \
    -scheme PhoneRunner -destination "id=$UDID" -derivedDataPath "$RUNNER/dd" \
    -allowProvisioningUpdates >"$OUT/runner-build.log" 2>&1 ||
    { grep -E "error:" "$OUT/runner-build.log" | tail -10 >&2; echo "phone: runner build failed" >&2; exit 1; }
  # Keep XCTest's screen recording of EVERY run, not only failed ones: a glitch that is on
  # screen for a moment is found in the video of a run that passed.
  local run=("$RUNNER"/dd/Build/Products/*.xctestrun)
  plutil -replace UITests.SystemAttachmentLifetime -string keepAlways "${run[0]}"
  echo "phone: runner built" >&2
}

# run_steps <steps> <result dir>: one runner session; files its screenshots by journey.
run_steps() {
  local steps="$1" dir="$2"
  local run=("$RUNNER"/dd/Build/Products/*.xctestrun)
  [ -f "${run[0]}" ] || { echo "phone: build the runner first (phone.sh runner)" >&2; exit 1; }
  mkdir -p "$dir"
  rm -rf "$dir/result.xcresult"
  local status=0
  TEST_RUNNER_STEPS="$steps" TEST_RUNNER_APP_BUNDLE_ID="$APP_BUNDLE_ID" \
    xcodebuild test-without-building -xctestrun "${run[0]}" \
    -destination "id=$UDID" -resultBundlePath "$dir/result.xcresult" >"$dir/xcodebuild.log" 2>&1 || status=$?
  # XCTest's own errors ("Failed to tap …") end the run mid-journey; keep them in order.
  grep -E "^(JOURNEY|END|OK|FAIL|SKIP|ID|TEXT|DIAG) |<<<DUMP|DUMP>>>|^ +[A-Za-z]+, 0x|: error: -\[UITests" \
    "$dir/xcodebuild.log" | sed -E 's/^.*: error: -\[UITests\.Steps testJourney\] : /XCTEST /' >"$dir/steps.log" || true
  xcrun xcresulttool export attachments --path "$dir/result.xcresult" --output-path "$dir/.shots" >/dev/null 2>&1 || true
  # In the order taken: "<journey>--<name>" shots to <dir>/<journey>/NN-<name>.png, the screen
  # recording to <dir>/recording.mp4 (+ .json with when it started); XCTest's own snapshots dropped.
  if [ -f "$dir/.shots/manifest.json" ]; then
    node -e '
      const fs = require("fs"), path = require("path"), [src, dst] = process.argv.slice(1);
      const m = JSON.parse(fs.readFileSync(path.join(src, "manifest.json"), "utf8"));
      const all = m.flatMap((t) => t.attachments ?? []).sort((a, b) => a.timestamp - b.timestamp);
      const count = {};
      let rec = 0;
      for (const a of all) {
        const from = path.join(src, a.exportedFileName);
        if (!fs.existsSync(from)) continue;
        const human = (a.suggestedHumanReadableName ?? "").replace(/_\d+_[0-9A-F-]+(\.\w+)$/i, "$1");
        if (/^Screen Recording/.test(human)) {
          const name = rec++ ? `recording-${rec}` : "recording";
          fs.renameSync(from, path.join(dst, `${name}.mp4`));
          fs.writeFileSync(path.join(dst, `${name}.json`), JSON.stringify({ attachedAt: a.timestamp }));
          continue;
        }
        if (!human.includes("--")) continue;
        const [j, n] = human.split("--");
        fs.mkdirSync(path.join(dst, j), { recursive: true });
        count[j] = (count[j] ?? 0) + 1;
        fs.renameSync(from, path.join(dst, j, String(count[j]).padStart(2, "0") + "-" + n));
      }
    ' "$dir/.shots" "$dir"
    rm -rf "$dir/.shots"
  fi
  if [ $status -ne 0 ] && ! grep -q "^FAIL " "$dir/steps.log"; then
    echo "FAIL runner (see $dir/xcodebuild.log)" | tee -a "$dir/steps.log"
    grep -E "error|Error" "$dir/xcodebuild.log" | tail -5
  fi
  return $status
}

# A journey file: one step per line, "#" starts a comment.
steps_of() { grep -v '^\s*#' "$1" | sed -E 's/[[:space:]]+#.*$//' | grep -v '^\s*$' | paste -sd'|' -; }

# Every chosen journey in ONE runner session (one ~20 s start-up, not one per journey).
test_journeys() {
  need_phone
  need_unlocked
  local dir names=("$@") all="" file
  dir="$OUT/runs/$(date +%Y%m%d-%H%M%S)"
  if [ ${#names[@]} -eq 0 ]; then
    while IFS= read -r f; do names+=("$(basename "$f" .steps)"); done < <(ls "$HERE"/journeys/*.steps | sort)
  fi
  # Every run starts from the same fake data, when the project has a test server and a seed.
  if [ -n "${API_PORT:-}" ] && [ -x "$HERE/scripts/seed.sh" ] && [ "${NO_SEED:-0}" != 1 ]; then
    if curl -fsS "http://127.0.0.1:$API_PORT${HEALTH_PATH:-/health}" >/dev/null 2>&1; then
      QUICK=1 "$HERE/scripts/seed.sh" "$OUT/state" 2>/dev/null || echo "phone: warning: seed failed" >&2
    else
      echo "phone: warning: no test server on :$API_PORT" >&2
    fi
  fi
  for name in "${names[@]}"; do
    file=$(ls "$HERE"/journeys/*"${name%.steps}".steps 2>/dev/null | head -1)
    [ -f "$file" ] || { echo "phone: no journey $name" >&2; exit 2; }
    all+="journey:$(basename "$file" .steps)|$(steps_of "$file")|"
  done
  echo "phone: ${#names[@]} journeys on the iPhone; results in $dir" >&2
  local started=$SECONDS
  run_steps "$all" "$dir" || true
  echo "phone: run took $((SECONDS - started)) s" >&2
  summary "$dir/steps.log"
}

# Per journey: passed or the first failure (with the app's last trail lines), and anything
# slow: a screen over 1.5 s after the step began, or an API call over 1 s (trail "ms=").
summary() {
  node -e '
    const lines = require("fs").readFileSync(process.argv[1], "utf8").split("\n");
    const res = []; let cur;
    for (const l of lines) {
      if (l.startsWith("JOURNEY ")) res.push(cur = { name: l.slice(8), fail: null, end: false, slow: [], diag: [] });
      else if (!cur) continue;
      else if (l.startsWith("END ")) cur.end = true;
      else if (l.startsWith("FAIL ") && !cur.fail) cur.fail = l.slice(5);
      else if (l.startsWith("XCTEST ") && !l.startsWith("XCTEST failed - ") && !cur.fail) cur.fail = "runner stopped: " + l.slice(7);
      else if (l.startsWith("DIAG ")) {
        cur.diag.push(l.slice(5));
        const ms = / ms=(\d+)/.exec(l);
        if (ms && Number(ms[1]) > 1000) cur.slow.push("api " + l.slice(5));
      } else if (l.startsWith("OK ")) {
        const m = / (\d+)ms$/.exec(l);
        if (m && Number(m[1]) > 1500 && /^OK (expect|see|either|gone):/.test(l)) cur.slow.push(l.slice(3));
      }
    }
    for (const r of res) if (!r.end && !r.fail) r.fail = "runner stopped before the end (see xcodebuild.log)";
    for (const r of res) {
      console.log(`${r.fail ? "✗" : "✓"} ${r.name}${r.fail ? "  — " + r.fail : ""}`);
      for (const s of r.slow) console.log(`    slow: ${s}`);
      if (r.fail) for (const d of r.diag.slice(-10)) console.log(`    app: ${d}`);
    }
    const bad = res.filter((r) => r.fail).length;
    console.log(`\nphone: ${res.length - bad} passed, ${bad} failed`);
    process.exit(bad || !res.length ? 1 : 0);
  ' "$1"
}

cmd="${1:-test}"
shift || true
case "$cmd" in
  build) build_app ;;
  runner) build_runner ;;
  test) test_journeys "$@" ;;
  steps)
    need_phone
    need_unlocked
    d="$OUT/adhoc/$(date +%H%M%S)"
    st=0; run_steps "${1:?steps}" "$d" || st=$?
    cat "$d/steps.log"; exit $st
    ;;
  shot)
    need_phone
    mkdir -p "$OUT/shots"
    xcrun devicectl device capture screenshot --device "$UDID" \
      --destination "$OUT/shots/${1:-now}.png" >/dev/null && echo "$OUT/shots/${1:-now}.png"
    ;;
  launch) need_phone; xcrun devicectl device process launch --terminate-existing --device "$UDID" "$APP_BUNDLE_ID" >/dev/null && echo launched ;;
  link)
    need_phone
    : "${APP_SCHEME:?set APP_SCHEME (the deep-link scheme) in phone.env}"
    xcrun devicectl device process launch --terminate-existing --device "$UDID" \
      --payload-url "$APP_SCHEME://${1:?path}" "$APP_BUNDLE_ID" >/dev/null && sleep "${2:-3}" && echo "opened $APP_SCHEME://$1"
    ;;
  *) echo "usage: phone.sh build|runner|test [journey…]|steps '<a|b>'|shot [name]|launch|link <path> [s]" >&2; exit 2 ;;
esac
