# The Android phone

`tools/android.sh` drives a real Android phone over adb. There's no runner to build: taps go through `adb shell input`, and the screen is read from the accessibility tree (`uiautomator dump`). A React Native `testID` shows up there as `resource-id`, and an `accessibilityLabel` as `content-desc`. That's how `ids`, `tap <testID>` and `trail` work. The trail is the same invisible element the iPhone runner reads.

For installing the SDK, the `android` CLI, device commands and official Android docs, load the official **`android-cli`** skill. For testing strategy in native Android code, load **`testing-setup`**. This file holds only what the two-phone work taught.

## Commands

```sh
android.sh build             # Release, JS inside, test server baked in, installed
android.sh awake             # screen stays on 10 min (prints how to restore the old value)
android.sh launch | restart
android.sh ids               # testIDs on screen, with label and bounds
android.sh tap home-add      # waits up to 10 s for it; refuses when the app is not in front
android.sh type 123456       # ASCII only
android.sh trail             # the app's diagnostics trail
android.sh shot home
android.sh rec open-sheet 8  # timestamped recording, then: node framegaps.mjs …/open-sheet.mp4
android.sh log 15            # logcat of the app's own process only
android.sh notif             # the app's own notifications: channel, importance, style
```

## Lessons

- **Build with JDK 17.** A newer default JDK breaks Gradle. `android.sh build` picks 17 through `/usr/libexec/java_home -v 17`.
- **Regenerate `android/` every build** (`expo prebuild -p android`). The app config is the source of truth, for example cleartext allowed only for an http test server.
- **Run a Release build before you trust Android.** Release builds are minified. Libraries whose native code looks up Java classes by name (WebRTC in `JNI_OnLoad`, for example) crash at launch when R8 renames those classes. Debug builds never show it. Fix it with keep rules (`expo-build-properties` → `android.extraProguardRules`), not by turning off minification.
- **Taps are coordinates.** When another app is in front (the launcher, a system dialog), the tap lands there. `tap` checks `front` first.
- **`input text` is ASCII.** Arabic and other non-Latin text can't be typed this way. Fake data with Latin names keeps journeys typeable. For number fields, also accept Arabic-Indic digits in the app (`ascii-capable-number-pad` on iOS; normalise digits on input).
- **The screen sleeps.** A dozing phone or a lock screen makes every dump empty and every screenshot black. Run `android.sh awake` at the start of a session. If the phone is locked, ask the user to unlock it. **Never type the PIN.**
- **Read only the app's own data.** Logcat with `--pid` of the app (`android.sh log`), crash-buffer lines filtered to the app's package, `appops` queried only for the app, notification records only for the app's package. Don't expand the notification shade: it shows the user's other apps.
- **Proving a privacy behaviour.** For example, "the mic is not on while it rings": sample `adb shell cmd appops get <package> RECORD_AUDIO` each second during the moment. It says `running` while the app holds the mic.
- **120 Hz phones.** Many Android phones render at 120 Hz, so one frame is about 8 ms. `android.sh rec` uses `screenrecord --bugreport` (a frame only when the screen changes, with the phone's time on each one). `framegaps.mjs` then reads ffprobe's frame timestamps for the window of a transition and counts gaps over 1.5 refresh intervals. `sheets.mjs` lays the same video out as contact sheets.
- **`screenrecord` stops at 180 s.** For longer scenarios, record in segments and keep each start time.
