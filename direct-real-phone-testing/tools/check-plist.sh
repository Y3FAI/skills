#!/usr/bin/env bash
# A built iOS app must carry every permission text (Info.plist *UsageDescription) the Expo app
# config declares after its plugins. ios/ is generated and usually gitignored; when it is older
# than app.config a key is missing, and iOS KILLS the app the moment it asks for that
# permission. It looks like a crash on a button ("share broke"). Run it on every build you test.
#
#   check-plist.sh <path/to/App.app | ios/<App>/Info.plist>
set -euo pipefail

APP="${1:?usage: check-plist.sh <path/to/App.app | Info.plist>}"
PLIST="$APP"
[ -d "$APP" ] && PLIST="$APP/Info.plist"
HERE="$(cd "$(dirname "$0")/.." && pwd)"   # e2e/phone
ROOT="$(cd "$HERE/../.." && pwd)"
# shellcheck disable=SC1091
[ -f "$HERE/phone.env" ] && . "$HERE/phone.env"
want=$(cd "$ROOT/${MOBILE_DIR:-apps/mobile}" && npx expo config --type introspect --json 2>/dev/null)
have=$(plutil -convert json -o - "$PLIST")

WANT="$want" HAVE="$have" node -e '
  const want = JSON.parse(process.env.WANT).ios?.infoPlist ?? {};
  const have = JSON.parse(process.env.HAVE);
  const keys = Object.keys(want).filter((k) => /UsageDescription$/.test(k));
  const bad = keys.filter((k) => have[k] !== want[k]);
  if (bad.length) {
    console.error("check-plist: the built app is older than the app config:");
    for (const k of bad) console.error(`  ${k}: ${have[k] === undefined ? "missing" : "different text"}`);
    console.error("Regenerate it (npx expo prebuild -p ios), then rebuild.");
    process.exit(1);
  }
  console.error(`check-plist: ${keys.length} permission texts match the app config`);
'
