#!/usr/bin/env node
// Frame gaps in a screen recording: did a transition run at the display's rate, or drop
// frames? Made for Android's `screenrecord --bugreport` (android.sh rec), which writes a frame
// only when the screen changes: during an animation the gaps should be one refresh interval
// (8.3 ms at 120 Hz, 16.7 ms at 60 Hz). Give it the window of the move, not a still screen.
//
//   node framegaps.mjs <video.mp4> [--from 2.0] [--to 3.5] [--hz 120]
//
// Prints the frames in the window, the median gap, every gap over 1.5 refresh intervals
// (a dropped frame or more) and the longest. Needs ffprobe.
import { spawnSync } from "node:child_process";

const args = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = args.indexOf(name);
  if (i < 0) return fallback;
  const [, value] = args.splice(i, 2);
  return Number(value);
};
const from = opt("--from", 0), to = opt("--to", Infinity), hz = opt("--hz", 120);
const file = args[0];
if (!file) {
  console.error("usage: framegaps.mjs <video.mp4> [--from s] [--to s] [--hz 120]");
  process.exit(2);
}
const out = spawnSync("ffprobe", ["-v", "error", "-select_streams", "v:0", "-show_entries",
  "frame=pts_time", "-of", "csv=p=0", file], { encoding: "utf8", maxBuffer: 1 << 26 }).stdout;
const times = out.split("\n").map(Number).filter((t) => Number.isFinite(t) && t >= from && t <= to);
if (times.length < 2) { console.log("fewer than 2 frames in that window"); process.exit(1); }
const gaps = times.slice(1).map((t, i) => (t - times[i]) * 1000);
const sorted = [...gaps].sort((a, b) => a - b);
const interval = 1000 / hz;
const late = gaps.map((g, i) => [g, times[i + 1]]).filter(([g]) => g > interval * 1.5);
console.log(`${times.length} frames in ${(times.at(-1) - times[0]).toFixed(2)} s; ` +
  `median gap ${sorted[sorted.length >> 1].toFixed(1)} ms (one refresh at ${hz} Hz: ${interval.toFixed(1)} ms)`);
console.log(`${late.length} gaps over ${(interval * 1.5).toFixed(1)} ms; longest ${sorted.at(-1).toFixed(1)} ms`);
for (const [g, t] of late.slice(0, 20)) console.log(`  ${t.toFixed(3)} s: ${g.toFixed(1)} ms (~${Math.round(g / interval) - 1} dropped)`);
