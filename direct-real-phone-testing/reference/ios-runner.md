# The iPhone runner

`tools/runner` is an XcodeGen spec: an empty host app plus a UI-test bundle (`UITests/Steps.swift`). The bundle drives the **installed** app by bundle id. `phone.sh` passes it the steps and the bundle id through `TEST_RUNNER_*` environment variables and runs it with `xcodebuild test-without-building`. The runner is built once (`phone.sh runner`). The app is built separately (`phone.sh build`), so changing the app never rebuilds the runner, and changing a journey rebuilds nothing.

Apple's `device-interaction` skill (it ships with Xcode, through the Xcode MCP tools) is the other way to touch a phone: an agent session that installs, taps and screenshots interactively. Use it for exploring. Use this runner for repeatable journeys you run again after every change, with timings, the app's trail and a screen recording.

## Writing journeys

The full step list is at the top of `Steps.swift`. Read it there, because it's the version that runs. The basics:

- Start every journey with `launch` (a fresh start that keeps state), then `timeout:20` for the first screen, then `timeout:10`.
- **Wait for what proves the screen is there**: `expect:<testID>`, `see:<text>`, `trail:<event>`. Never `wait:` for something that will appear: it's slow when the app is fast and flaky when it's slow. Keep `wait:` for real time, such as a composer sliding up before you take its shot.
- `shot:name` at stable checkpoints. Shots land in `.out/runs/<time>/<journey>/NN-name.png`, in order.
- `?step` for something that only sometimes appears (a first-run prompt). It counts as SKIP, not FAIL.
- `sys:Don't Allow/Not Now` for system prompts. They belong to SpringBoard, not the app.
- `ids` and `texts` print what is on screen. `dump` prints the whole tree. Start a new journey from these, not from guesses.

## What a run tells you

- `OK <step> <ms>`: the time from the step's start until the screen showed it. The summary flags a screen over 1.5 s and an API call over 1 s (from the trail's `ms=`).
- `FAIL <step> (why)`: plus a screenshot named FAIL and the app's last trail lines. The rest of that journey is skipped, and the next one starts.
- `DIAG …`: the app's own trail, printed at every journey's end and after every failure.
- A journey passed only if it reached `END`. When XCTest itself throws (an ambiguous match, an element gone mid-tap), the run stops without a FAIL line. The summary reports that as "runner stopped", not as a pass.
- `recording.mp4`: XCTest's screen recording of the whole run, kept even when everything passed (`phone.sh runner` sets `SystemAttachmentLifetime keepAlways`). Watch it, or make contact sheets from it (see [motion-and-recording.md](motion-and-recording.md)), to catch what a screenshot can't: a flash of an empty list, a jump at the end of a transition.

## Lessons that cost hours (keep them)

- **60 s per tap.** XCTest waits for the app to be "idle" before every event, and React Native (new architecture) never sends that signal. The runner swizzles `XCUIApplicationProcess`'s quiescence wait into a no-op (`setUp` in Steps.swift). Every step then waits for its own element, which is also what makes the timings mean something.
- **Poll every 100 ms, one snapshot per check.** `waitForExistence` checks about once a second. `exists`, `isHittable` and `frame` are three separate queries, and an element that leaves in between (a sheet closing itself) is an exception that ends the whole run.
- **Tap only a still target.** A sheet rising with the keyboard gets the tap where it *was*. `tap:` waits until the frame is the same on two polls, then taps those coordinates.
- **A tap on a gliding list only stops it.** `scrollto:` waits for the list to come to rest. Without that, an invite button "did nothing".
- **Type one character at a time** (0.12 s). Controlled React Native fields drop faster typing. For Arabic and other complex scripts, check the field's value afterwards with `see:`.
- **System buttons: take the first match.** iOS 27's contacts prompt has two "Don't Allow" buttons, and a unique match threw and ended the run.
- **Apple's message composer runs in another process** (`com.apple.MobileSMS.compose`). `sys:` looks there too, but on iOS 27 its buttons were out of reach. Close it by position (`point:x,y`, found from a screenshot of that phone model) and check what the app received through the trail (`trail:invite.done result=cancelled`). **Never press send.**
- **All journeys in one session.** Starting the runner takes about 20 s. `phone.sh test` joins every journey into one step list and splits the results back out by journey.
- **A locked phone can't be driven.** `phone.sh` waits up to 2 minutes for the user to unlock it. Never ask for the passcode and never type it.
- **One heavy build at a time.** Two `xcodebuild`s, or an app build alongside the runner build, fight over DerivedData and the phone.

## The permission-text check

`ios/` is generated and usually gitignored. If it's older than `app.config`, a `*UsageDescription` key is missing, and iOS **kills** the app the moment it asks for that permission. That looks like "the share button crashes". `check-plist.sh` compares the built app with `npx expo config --type introspect`, and `phone.sh build` regenerates `ios/` when they differ. If a crash happens right on a permission prompt, run it first.

## Handy one-offs

```sh
phone.sh steps 'ids'                       # what testIDs are on screen
phone.sh steps 'other:com.apple.springboard'   # a system screen's tree (prompts, banners)
phone.sh shot now                          # screenshot without the runner (devicectl)
phone.sh link 'item/12' 3                  # open a screen by deep link
xcrun devicectl device info apps --device <udid> | grep -i <name>   # is it installed?
```

Crash reports from the phone (read only the app's own; they are named `<AppName>-<date>.ips`):

```sh
xcrun devicectl device info files --device <udid> --domain-type systemCrashLogs | grep '^<AppName>-'
xcrun devicectl device copy from --device <udid> --domain-type systemCrashLogs \
  --source <AppName>-YYYY-MM-DD-HHMMSS.ips --destination .out/<AppName>.ips
```
