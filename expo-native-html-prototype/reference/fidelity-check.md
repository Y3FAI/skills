# Does the app match the prototype?

Check each platform separately, against the prototype in that platform's mode. Then ask the second question: does it feel like the platform's own apps?

## 1. Still screens, side by side

1. Shoot the prototype's states: `node tools/shoot.mjs prototype.html proto set:platform=ios shot:home click:#fab wait:600 shot:add …` (2× PNGs of the phone only).
2. Shoot the same states on the phone (`direct-real-phone-testing`: journeys with `shot:` steps, or `phone.sh shot`).
3. Put each pair side by side at the same width: `ffmpeg -i proto/home.png -i run/home.png -filter_complex "[0]scale=600:-1[a];[1]scale=600:-1[b];[a][b]hstack" home-vs.png`.
4. Read every pair and list the differences: spacing, type size and weight, colours, corner radii, blur and translucency, icon weight, what sits at the bottom vs the top. Fix them, or ask the user when a platform convention should win.

## 2. Motion, on the phone

Screenshots can't show a transition. For each transition in the prototype (push, back, each sheet, the grow and shrink, keyboard up/down):
1. Record it on the phone (`direct-real-phone-testing`: the iPhone runner's recording, `android.sh rec`).
2. Look at contact sheets (`sheets.mjs --fps 12` over the window of the move). Check that it starts from where the finger was, nothing flashes or jumps, text doesn't re-wrap, bars change with the move, and it ends without a bump.
3. Measure: hitches and hangs on the iPhone (`smooth.sh`), frame gaps on Android (`framegaps.mjs`). A transition that drops frames on a 120 Hz phone needs transforms instead of layout.
4. Compare the timing with the prototype's slow-motion run. The app should take the same time with the same curve.

## 3. Native feel

Open the platform's own apps (Settings, Messages, Photos on iPhone; Settings, Messages, Photos on Android) and do the same kind of action. The sheet, the back gesture, the press feedback and the haptic should feel like theirs. Anything that doesn't is usually a hand-made imitation of a component the platform already has (see native-mapping.md).

Report to the user with the side-by-side images and contact sheets, what you fixed, and what needs their decision.
