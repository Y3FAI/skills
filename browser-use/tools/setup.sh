#!/usr/bin/env bash
# Set up the BiDi driver for the user's own Zen / Firefox.
# Installs puppeteer-core (no bundled browser) into ~/.cache/browser-use,
# patches it to treat Zen as Firefox, and copies the driver next to it.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DIR="${BROWSER_USE_HOME:-$HOME/.cache/browser-use}"
mkdir -p "$DIR"
cd "$DIR"
[ -f package.json ] || npm init -y >/dev/null
npm i puppeteer-core@24.10.0 >/dev/null 2>&1

# Zen reports browserName "zen", so Puppeteer thinks it is Chrome and subscribes
# to goog:cdp events -> "Module goog:cdp does not exist". Make it match zen too.
B=node_modules/puppeteer-core/lib/esm/puppeteer/bidi
perl -pi -e "s/\.includes\('firefox'\)/.match(\/firefox|zen\/i)/g" "$B/Browser.js" "$B/BrowserConnector.js"
grep -q 'firefox|zen' "$B/Browser.js" || { echo "patch failed: Puppeteer layout changed" >&2; exit 1; }

cp "$HERE/bidi-driver.mjs" "$DIR/bidi-driver.mjs"
echo "ready: node $DIR/bidi-driver.mjs"
