---
name: direct-real-phone-testing
description: Test a mobile app (Expo / React Native, iOS and Android) directly on the user's real, connected iPhone and Android phone from the terminal, never a simulator or emulator. Release builds with the JS inside, an XCUITest runner that walks scripted journeys by testID with timings, the app's own diagnostics trail, screenshots, full-run screen recordings, contact sheets, frame gaps and Instruments hitches/hangs, a local test server with fake data, and two-phone scenarios. Use whenever the user wants to test, verify, check, record or measure the app "on my phone", "on device", "on the real iPhone/Android", asks "does it work?" after a UI change, reports a bug only seen on their phone, wants journeys or smoke tests run on hardware, wants transitions checked for smoothness, or wants this phone-testing lane set up in a new project, even if they don't say "real phone testing".
---

# Direct real-phone testing

Drive the user's own phones from the Mac: build the Release app, install it, walk journeys, and come back with screenshots, timings, the app's trail and a screen recording. A simulator's GPU, audio, keyboard, contacts and display rate are the Mac's. Real bugs (a permission crash, a stripped class, a stutter at 120 Hz) only show on the phone, so **never use a simulator or emulator** for this.

This skill is the glue and the lessons. The tools it calls change faster than it does, so the official skills below are the source of truth for their commands.

## Official skills: load them, keep them fresh

| Skill | Source | Load it for |
|---|---|---|
| `device-interaction` | Apple, ships with Xcode | interactive device sessions through the Xcode MCP tools (explore, screenshot, tap) |
| `xctrace` | Apple, ships with Xcode | anything Instruments: traces, hitches, hangs, reading `.trace` files |
| `android-cli` | `android/skills` | installing the SDK and `android` tool, devices, screenshots, UI inspection, official docs |
| `testing-setup` | `android/skills` | test strategy and harnesses inside native Android code |
| `expo-dev-client` | `expo/skills` | dev builds for fast UI iteration (this lane verifies on Release) |
| `eas-app-stores` | `expo/skills` | TestFlight / Play internal testing when the phone is not at the Mac |
| `expo-animation` | `expo/skills` | how motion should be built; this skill only checks the result |

**Before relying on one, update it.** Install skills per project, into the repo, not globally:

```sh
npx skills@latest add android/skills -a universal claude-code -y -s android-cli testing-setup
npx skills@latest add expo/skills   -a universal claude-code -y -s expo-dev-client expo-animation
npx skills@latest update -p        # refresh every project skill (run it at the start of a testing session)
```

Apple's skills aren't on GitHub. They ship inside Xcode, so after each Xcode update, copy them out again. In `Xcode.app/Contents/PlugIns/IDEIntelligenceChat.framework/Versions/A/Resources/`, `<name>.idechatprompttemplate` is the `SKILL.md` and each `<name>-ref-<topic>.md.packaged` is `references/<topic>.md`. Copy them into the project's `.agents/skills/<name>/`, and don't publish them. When an official skill and this one disagree about a tool's flags, the official skill wins. Then fix this skill.

## The lane at a glance

```
e2e/phone/  phone.env · journeys/*.steps · motion/everyday.steps · runner/ · scripts/ · .out/ (gitignored)
```

| Command | Does |
|---|---|
| `phone.sh build` | Release build (JS inside, test server and `EXPO_PUBLIC_DIAG=1` baked in), permission texts checked, installed on the iPhone |
| `phone.sh runner` | builds the XCUITest runner once (and after `Steps.swift` changes) |
| `phone.sh test [journey…]` | every journey in one runner session, then a summary: ✓/✗, slow screens, the app's trail on failure |
| `phone.sh steps '<a\|b\|c>'` | ad-hoc steps (`ids`, `texts` and `dump` show what's on screen) |
| `phone.sh shot` / `launch` / `link <path>` | screenshot, (re)start, deep link |
| `android.sh build\|ids\|tap\|trail\|shot\|rec\|log\|notif\|awake` | the Android phone over adb |
| `smooth.sh` | Instruments hitches and hangs while the runner moves |
| `sheets.mjs` / `framegaps.mjs` | contact sheets from recordings / frame gaps in a transition |

Every run lands in `.out/runs/<time>/`: `<journey>/NN-shot.png`, `recording.mp4`, `steps.log` (each step with its time, plus `DIAG` lines).

## Workflow

1. **Is the lane there?** Look for `e2e/phone/` (or the project's own phone scripts and README). If it's missing, set it up from [reference/setup.md](reference/setup.md) with the templates in `tools/`. Copy them into the project and fill in `phone.env`. Show the user the plan first: it touches the app (testIDs, the trail) and needs their phone settings changed.
2. **Phones ready?** `xcrun devicectl list devices` / `adb devices`. If a phone is locked, ask the user to unlock it, and wait. If it's missing, ask them to connect it.
3. **Build only what changed.** App code or config changed → `phone.sh build` (one heavy build at a time). Only `Steps.swift` changed → `phone.sh runner`. Only journeys changed → nothing.
4. **Run** the journeys that cover the change, then all of them before calling it done.
5. **Look.** Read `steps.log` and the summary, open every screenshot you're reporting on (Read the PNG), and check the recording's contact sheets around anything that changed. A green run with a wrong screen is still a failure.
6. **Report** to the user: what passed, what failed (the step, the screenshot, the trail lines), anything slow (over 1.5 s for a screen, 1 s for an API call), and anything the recording showed. Include paths to the shots.

When a step fails, find out why before changing the journey: `ids` on that screen, the FAIL screenshot, the trail. Fix the app when the app is wrong. Loosening the journey hides the bug.

## Rules that protect the user

- **Fake data only.** The test build talks to a local server seeded with generated data ([reference/test-server.md](reference/test-server.md)). Never production, never a real person's data in a screenshot.
- **Never send anything.** Composers (SMS, mail, share) opened by a journey get cancelled. Real-looking fake numbers are still someone's number.
- **The user's own data stays on the phone.** Refuse contacts, photos and files prompts in journeys unless the user asks otherwise. Read only the app's own logs, notifications, crash reports and app-ops, never other apps'. Don't open the notification shade or Control Center to read it.
- **Never type the passcode or PIN.** Ask the user to unlock.
- **The trail carries no personal data:** statuses, timings and error codes. No numbers, names, tokens, message bodies or error messages.
- **Don't work around a denied permission prompt or tool.** Ask the user.

## Reference

- [reference/setup.md](reference/setup.md): first-time setup (Mac, iPhone Developer Mode and UI Automation, adb, JDK 17, testIDs, the trail, http test builds), and why Release.
- [reference/ios-runner.md](reference/ios-runner.md): how the runner works, writing journeys, reading a run, the lessons (60 s taps, still targets, gliding lists, composers, permission-text crashes), crash reports.
- [reference/android.md](reference/android.md): the adb lane and its lessons (JDK, minification, ASCII typing, screen sleep, 120 Hz).
- [reference/test-server.md](reference/test-server.md): the Mac-hosted backend and the fake data.
- [reference/motion-and-recording.md](reference/motion-and-recording.md): recordings, contact sheets, frame gaps, Instruments thresholds.
- [reference/two-phones.md](reference/two-phones.md): scenarios between an iPhone and an Android (calls, messages), clocks, and the judge.

Tools: `tools/phone.sh`, `tools/android.sh`, `tools/check-plist.sh`, `tools/smooth.sh`, `tools/sheets.mjs`, `tools/framegaps.mjs`, `tools/runner/` (XcodeGen spec + `Steps.swift`, the step list is at its top), `tools/app/diag.ts` + `diag-probe.tsx`, `tools/journeys/01-home.steps`, `tools/phone.env.example`.

Related: `expo-native-html-prototype` (the prototype the phone is checked against) and `project-blueprint` (where this lane sits in a project's docs and testing layers).

Proven on Xcode 27.2, iOS 27, Expo SDK 58 / React Native 0.88, an iPhone 16e and a Galaxy S22 (2026-11). If a newer version breaks something, check the official skills, then update the lesson here.
