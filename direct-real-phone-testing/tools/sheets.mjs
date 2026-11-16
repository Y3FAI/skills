#!/usr/bin/env node
// Contact sheets from screen recordings, for finding what is on screen for a moment only (a
// flash of an empty list, a wrong label for 200 ms, a jump at the end of a transition). Each
// sheet is 6 s of one video at 4 frames a second, 8 × 3, read row by row. A phone.sh run's
// recording.mp4 has a recording.json with its start, so its sheets are named by wall-clock
// time and line up with steps.log and with another phone's sheets.
//
//   node sheets.mjs <run folder | video.mp4 …> [--from HH:MM:SS] [--to HH:MM:SS] [--fps 4]
//
// Writes sheets/<video>-<HHMMSS.s or +SSS.s>.png next to each video. Needs ffmpeg/ffprobe.
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const args = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = args.indexOf(name);
  if (i < 0) return fallback;
  const [, value] = args.splice(i, 2);
  return value;
};
const from = opt("--from"), to = opt("--to"), fps = Number(opt("--fps", "4"));
if (!args.length) {
  console.error("usage: sheets.mjs <run folder | video.mp4 …> [--from HH:MM:SS] [--to HH:MM:SS] [--fps 4]");
  process.exit(2);
}
const SPAN = (8 * 3) / fps; // seconds per sheet

const day = (hms) => {
  const [h, m, s] = hms.split(":").map(Number);
  const d = new Date();
  d.setHours(h, m, 0, 0);
  return d.getTime() + s * 1000;
};
const duration = (file) =>
  Number(spawnSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file], { encoding: "utf8" }).stdout.trim());
const pad = (n, w = 2) => String(n).padStart(w, "0");
const stamp = (ms) => {
  const d = new Date(ms);
  return `${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}.${Math.floor(d.getMilliseconds() / 100)}`;
};

// Each video, and the wall-clock time of its first frame when a .json beside it says.
const videos = [];
for (const a of args) {
  const files = fs.statSync(a).isDirectory()
    ? fs.readdirSync(a).filter((f) => f.endsWith(".mp4")).map((f) => path.join(a, f))
    : [a];
  for (const file of files) {
    const meta = file.replace(/\.mp4$/, ".json");
    let start = null;
    if (fs.existsSync(meta)) {
      const { attachedAt } = JSON.parse(fs.readFileSync(meta, "utf8"));
      // XCTest's attachment time is when the recording started (seconds or ms since 1970).
      start = typeof attachedAt === "number" ? (attachedAt > 1e12 ? attachedAt : attachedAt * 1000) : Date.parse(attachedAt);
    }
    videos.push({ file, start });
  }
}

const lo = from ? day(from) : -Infinity;
const hi = to ? day(to) : Infinity;
let made = 0;
for (const v of videos) {
  const out = path.join(path.dirname(v.file), "sheets");
  fs.mkdirSync(out, { recursive: true });
  const base = path.basename(v.file, ".mp4");
  const len = duration(v.file);
  for (let t = 0; t < len; t += SPAN) {
    let name;
    if (v.start !== null) {
      const wall = v.start + t * 1000;
      if (wall + SPAN * 1000 < lo || wall > hi) continue;
      name = `${base}-${stamp(wall)}`;
    } else name = `${base}-+${pad(Math.floor(t), 3)}.${Math.round((t % 1) * 10)}`;
    const file = path.join(out, `${name}.png`);
    spawnSync("ffmpeg", ["-v", "error", "-y", "-ss", String(t), "-t", String(SPAN), "-i", v.file,
      "-vf", `fps=${fps},scale=150:-1,tile=8x3:padding=2:color=white`, "-frames:v", "1", file]);
    if (fs.existsSync(file)) made++;
  }
}
console.log(`${made} sheets (${SPAN} s each, ${fps} fps)`);
