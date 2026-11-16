# Recording the screen and judging motion

Screenshots catch layout. Recordings catch what's on screen for a moment only: an empty list flashing before the data, a label wrapping to two lines mid-transition, the status bar snapping dark too early, a jump when an animation ends. Measurements catch dropped frames you can't see at full speed.

## What to record

| Phone | How | Notes |
|---|---|---|
| iPhone, during journeys | XCTest's screen recording, always on | `.out/runs/<time>/recording.mp4` + `recording.json` (start time). Kept on a pass too. |
| iPhone, smoothness | `smooth.sh` (Instruments over xctrace) | Measures hitches and hangs. Don't judge iPhone smoothness from the video. |
| Android | `android.sh rec <name> <s>` | `screenrecord --bugreport`: phone time on each frame, a frame per change. Max 180 s. |

## Looking at a recording

1. **Contact sheets first.** `node sheets.mjs .out/runs/<time>` writes a sheet per 6 s (8 × 3 frames at 4 fps, row by row), named by wall-clock time, so a sheet lines up with `steps.log` and with the other phone. Read the sheets around each step. For a fast transition, use `--fps 12` with `--from`/`--to`.
2. **Single frames where a sheet looks wrong:** `ffmpeg -ss 12.4 -i recording.mp4 -frames:v 1 f.png`, or every frame of a window: `ffmpeg -ss 12 -t 1 -i rec.mp4 -vsync 0 frames/%03d.png` (`-vsync 0` keeps the real frames, with no duplicates).
3. **Frame gaps (Android):** `node framegaps.mjs rec.mp4 --from 2.0 --to 2.6 --hz 120` gives the median gap and every gap over 1.5 refresh intervals in the window of the move.

## Smoothness on the iPhone (`smooth.sh`)

Instruments' **Animation Hitches** template plus the **Hangs** instrument, on the running Release app, while the runner makes the moves in `motion/everyday.steps` (or you make them with `HAND=1`). Thresholds, from Apple:

- **Hitch time ratio:** under 5 ms/s good, 5–10 noticeable, over 10 bad.
- **Hangs:** over 100 ms is felt, over 250 ms is a microhang, over 500 ms a hang.

The trace stays in `.out/smooth/` for Instruments' timeline. For anything beyond these summaries (reading other tables, symbolication, the triage styles), load Apple's **`xctrace`** skill. It's the authoritative guide, and it's updated with Xcode.

## Judging motion

Measure it, then look at it, then decide. The numbers say whether frames dropped. The sheets say whether the motion is right: does it start where the finger was, does it end without a jump, does anything flash. For how motion *should* be built in Expo (springs, the UI thread, gesture handoff), load the official **`expo-animation`** skill. This skill only checks the result on the phone.

Simulators can't answer any of this: their GPU, display rate and touch are the Mac's.
