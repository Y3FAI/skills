#!/usr/bin/env bash
# Smoothness on the real iPhone, measured the way Apple does: Instruments' Animation Hitches
# template plus the Hangs instrument, on the running Release app while the runner makes the
# everyday moves (e2e/phone/motion/everyday.steps). Never a simulator: its GPU is the Mac's.
# Copy to <project>/e2e/phone/scripts/smooth.sh; settings come from e2e/phone/phone.env.
#
#   smooth.sh              the runner drives the app (phone.sh runner first)
#   HAND=1 smooth.sh       you drive it for SECONDS_LIMIT (default 45) seconds
#
# Reading it (Apple, "Understanding hitches in your app"): hitch time ratio under 5 ms/s is
# good, 5-10 ms/s is noticeable, over 10 ms/s is bad. Hangs: over 100 ms is felt, over
# 250 ms is a microhang, over 500 ms a hang. The xctrace skill (Apple's) has the details.
#
# Output: e2e/phone/.out/smooth/<time>.trace (open it in Instruments for the timeline).
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"   # e2e/phone
OUT="$HERE/.out/smooth"
# shellcheck disable=SC1091
[ -f "$HERE/phone.env" ] && . "$HERE/phone.env"
: "${APP_BUNDLE_ID:?set APP_BUNDLE_ID in phone.env}"
: "${APP_NAME:?set APP_NAME (the app process name, the Xcode product name) in phone.env}"
LIMIT="${SECONDS_LIMIT:-45}"
mkdir -p "$OUT"
TRACE="$OUT/$(date +%Y%m%d-%H%M%S).trace"

# The first connected iPhone (xctrace and devicectl agree on the UDID).
DEVICE="${PHONE_UDID:-$(xcrun xctrace list devices 2>/dev/null |
  awk '/^== Devices ==/{on=1;next} /^==/{on=0} on' |
  grep -E "\(([0-9]+\.)+[0-9]+\) \([0-9A-F-]{20,}\)$" | head -1 |
  sed -E 's/.*\(([0-9A-F-]+)\)$/\1/')}"
[ -n "$DEVICE" ] || { echo "smooth: no iPhone connected (cable or Wi-Fi, unlocked, trusted)" >&2; exit 1; }

xcrun devicectl device process launch --terminate-existing --device "$DEVICE" "$APP_BUNDLE_ID" >/dev/null
sleep 3
record() {
  xcrun xctrace record --template "Animation Hitches" --instrument Hangs \
    --device "$DEVICE" "$@" --time-limit "${LIMIT}s" \
    --output "$TRACE" --no-prompt >"$OUT/record.log" 2>&1 &
  REC=$!
  sleep 4 # the recorder attaches before the first move
}
echo "smooth: recording ${LIMIT}s" >&2
record --attach "$APP_NAME"
# Attaching by name sometimes fails at once; recording every process still works, and the
# hang triage below filters to the app.
if ! kill -0 "$REC" 2>/dev/null; then
  echo "smooth: attach failed ($(tail -1 "$OUT/record.log")); recording all processes" >&2
  rm -rf "$TRACE"
  record --all-processes
fi

if [ "${HAND:-0}" = 1 ]; then
  echo "smooth: make the everyday moves now (scroll, open a sheet, search, go back)" >&2
else
  steps=$(grep -v '^\s*#' "$HERE/motion/everyday.steps" | sed -E 's/[[:space:]]+#.*$//' | grep -v '^launch$' | grep -v '^\s*$' | paste -sd'|' -)
  PHONE_UDID="$DEVICE" bash "$HERE/scripts/phone.sh" steps "$steps" >"$OUT/motion.log" 2>&1 ||
    echo "smooth: a move failed; see $OUT/motion.log" >&2
fi
wait "$REC" || { tail -5 "$OUT/record.log" >&2; exit 1; }

show() { xcrun xctrace show "$TRACE" "$@" 2>/dev/null; }
echo
echo "== Hitches (frames that missed their deadline)"
show --track Hitches --summary "Summary: Hitches" | grep -v "focus destination\|^  \[list\]\|^$" || true
show --track Hitches --list "All Hitches" --format markdown | LIMIT="$LIMIT" node -e '
  const rows = require("fs").readFileSync(0, "utf8").split("\n").filter((l) => l.startsWith("|"));
  if (rows.length < 3) { console.log("hitch time ratio: 0 ms/s (no hitches)"); process.exit(0); }
  const head = rows[0].split("|").map((s) => s.trim());
  const col = head.findIndex((h) => /^(Hitch )?Duration$/i.test(h));
  if (col < 0) { console.log("hitch time ratio: see the summary (columns: " + head.join(", ") + ")"); process.exit(0); }
  const ms = (v) => { const m = /([\d.]+)\s*(ns|µs|us|ms|s)\b/.exec(v); if (!m) return 0;
    return Number(m[1]) * { ns: 1e-6, "µs": 1e-3, us: 1e-3, ms: 1, s: 1e3 }[m[2]]; };
  const total = rows.slice(2).reduce((a, r) => a + ms(r.split("|")[col] ?? ""), 0);
  const ratio = total / Number(process.env.LIMIT);
  const verdict = ratio < 5 ? "good" : ratio <= 10 ? "noticeable" : "bad";
  console.log(`hitch time ratio: ${ratio.toFixed(1)} ms/s (${verdict}; Apple: under 5 is good), ${rows.length - 2} hitches, ${total.toFixed(0)} ms in all`);
'
echo
echo "== Frame times"
show --track Display --summary "Summary: Average Frame Times" | grep -v "focus destination\|^  \[list\]\|^$" || true
echo
echo "== Hangs (main thread busy or blocked)"
xcrun xctrace triage "$TRACE" --style hangs --process "$APP_NAME" --limit 5 2>/dev/null ||
  show --track Hangs --summary "Summary: Hangs" || true
echo
echo "smooth: trace in $TRACE (open in Instruments for the timeline)"
