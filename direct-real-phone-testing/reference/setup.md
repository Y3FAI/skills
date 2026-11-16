# Setting up the phone lane in a project

Do this once per project. Afterwards a run is `phone.sh build` (after app changes), then `phone.sh test`.

## 1. The Mac and the phones

**iPhone**
- Xcode with your Apple ID signed in (Settings → Accounts). Any team works, a free one included. Its team id goes in `PHONE_TEAM_ID`.
- `brew install xcodegen` (it generates the runner's Xcode project, so nothing generated gets committed).
- The phone: connected by cable once, then "Trust This Computer". After that, Wi-Fi works too.
- On the phone: **Settings → Privacy & Security → Developer Mode** on (it restarts), then **Settings → Developer → Enable UI Automation** on. If UI Automation is off, the runner builds but can't drive anything.
- `xcrun devicectl list devices` shows the phone as `available (paired)`.

**Android**
- Android SDK platform-tools (`adb`) and **JDK 17** (`brew install --cask zulu@17`). Gradle fails with a newer default JDK.
- On the phone: Developer options → **USB debugging** on; allow the Mac when asked. `adb devices` shows `device`, not `unauthorized`.
- The official `android-cli` skill covers installing the SDK and the `android` tool.

## 2. Files in the project

```
e2e/phone/
  phone.env              this project's names (copy tools/phone.env.example); committed, no secrets
  journeys/*.steps       one step a line (start from tools/journeys/01-home.steps)
  motion/everyday.steps  the moves smooth.sh measures (scrolls, a sheet, search, back)
  runner/                copy of tools/runner/ (project.yml, Host/, UITests/Steps.swift)
  scripts/               phone.sh, android.sh, check-plist.sh, smooth.sh, sheets.mjs
  .out/                  gitignored: builds, runs, recordings, server state
```

- Add `e2e/phone/.out/` to `.gitignore`.
- Copy the scripts; don't symlink them into the skill. The project then keeps working when the skill changes, and a project-specific tweak stays in the project.
- Add package scripts so nobody has to remember paths, e.g. `"phone": "bash e2e/phone/scripts/phone.sh"`, `"phone:test": "bash e2e/phone/scripts/phone.sh test"`.
- Write a short `e2e/phone/README.md`: the commands, what a run prints, and this project's rules (fake data only, what never to press).

## 3. The app

**testIDs.** Journeys find things by `testID` (iOS: accessibility identifier; Android: resource-id). Give every control a journey touches a stable, readable one, such as `home-add`, `item-row-12` or `settings-signout`. Don't drive journeys by visible text when the app is translated. `see:` (label contains) is for checking content.

**The diagnostics trail.** Copy `tools/app/diag.ts` and `tools/app/diag-probe.tsx` into the app (for example `src/lib/`). Render `<DiagProbe />` once in the root layout. Call `diag("event", {key: value})` where the app does something a screenshot can't show: API calls (`path`, `status`, `ms`), a share sheet's result, an audio route, a socket state. The rules:
- It exists only in test builds (`EXPO_PUBLIC_DIAG=1`, which the build commands set). Store builds have none of it.
- Nothing leaves the phone. The runner reads one invisible element.
- Never put personal data in it. `mask()` hides ids and digit runs, but don't rely on it: log a status, never a body, and an error's `code` or class, never its message.

**A test build that talks to the Mac.** When the app has a backend, point the test build at a local server over Wi-Fi (see [test-server.md](test-server.md)). The address is baked in at build time (`EXPO_PUBLIC_*`), so changing the server means rebuilding. Plain http needs:
- Android: allow cleartext only when the API URL is http, so store builds keep the default. With `expo-build-properties`: `android: { usesCleartextTraffic: apiUrl.startsWith("http://") }`.
- iOS: Expo's generated Info.plist already allows local networking. If iOS asks for Local Network access, allow it, or the app can't reach the Mac.

## 4. First run

```sh
bash e2e/phone/scripts/phone.sh build     # Release build, JS inside, permission texts checked
bash e2e/phone/scripts/phone.sh runner    # signs and builds the runner (first time: Xcode may ask to register the phone)
bash e2e/phone/scripts/phone.sh steps 'ids'           # every testID on the screen now
bash e2e/phone/scripts/phone.sh test                  # every journey
```

If `runner` fails on signing, open `.out/runner/PhoneRunner.xcodeproj` once in Xcode, pick the team under Signing & Capabilities, and run `runner` again. Free teams need the bundle prefix to be unique: set `PHONE_RUNNER_BUNDLE_PREFIX`.

## Why a Release build

A debug build loads its JavaScript from Metro after launch, so the first screen waits on the bundler (20–40 s cold) and every timing measures the Mac. A Release build carries its JS and runs the way users get it, and it surfaces Release-only bugs: minification that strips classes native code looks up by name, missing permission texts, `console.log` dropped (only `console.error` survives in Release logs). Use a dev client (the official `expo-dev-client` skill) for fast UI iteration. Use this lane to verify.
