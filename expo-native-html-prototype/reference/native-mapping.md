# From prototype pieces to native components

Keep one look and give each platform its own mechanics. The prototype's iPhone and Android modes are the target for each. The APIs below were proven on Expo SDK 58 / React Native 0.88 (2026-11). Check the named official skill before using one, since APIs move.

| Prototype piece | iPhone | Android | Skill |
|---|---|---|---|
| Screens and push | Native stack (`expo-router` Stack, react-native-screens), default push | Native stack with the platform's push; don't borrow the iOS slide | `expo-router` |
| Back | Swipe back from the screen (native) | **Predictive back**: `android.predictiveBackGestureEnabled: true` in the app config. The system then previews the screen underneath | `navigation-event` |
| Bottom sheet (Add, edit name) | `presentation: "formSheet"`, `sheetAllowedDetents: "fitToContents"`, `sheetGrabberVisible: true`, `sheetCornerRadius` | Material `ModalBottomSheet` from `@expo/ui` (Jetpack Compose), with the React Native content inside `RNHostView` | `expo-ui` |
| Choice list (photo: camera / library / remove) | Action sheet or a small form sheet | `@expo/ui` bottom sheet with one row per choice (minimum height 56 dp) | `expo-ui` |
| Destructive confirm | Alert | Alert (a Material dialog is the right form) | |
| Picture grows into its screen | `presentation: "transparentModal"`, `animation: "none"`, gestures off; the screen draws its own move from the measured source frame | The same modal, with the move done in **transforms** (scale + translate), not layout props | `expo-animation` |
| Top bar | Native header: centred title, back chevron | Material top app bar: 64 dp, title at the start, back arrow | `expo-native-ui` |
| Press feedback | Dim while held (Reanimated CSS transition, ~120 ms); no scale | `Pressable android_ripple={{ color, foreground: true }}`; no scale | `expo-animation` |
| Haptics | `expo-haptics` impact/notification | `Haptics.performAndroidHapticsAsync(AndroidHaptics.Confirm / Reject / …)`: Android's own constants. iOS-style vibrations feel weak or wrong | `expo-native-ui` |
| Frosted + / frosted bar | `expo-blur` `BlurView` (`tint="systemUltraThinMaterialLight"`, high intensity) plus a light overlay | A real blur needs `BlurTargetView` around the content behind it, with `<BlurView blurTarget={ref} blurMethod="dimezisBlurViewSdk31Plus">` **outside** that target. Without it, "frosted" is plain translucent white. Or use an honest tinted surface (Material) | `expo-native-ui` |
| System bars | Status bar style per screen | Edge-to-edge. `expo-navigation-bar` plugin `{ enforceContrast: false }` so no grey scrim band; style the bar per screen | `edge-to-edge` |
| Keyboard | Sheets and fields rise with it (`KeyboardAvoidingView behavior="padding"`) | The same, with edge-to-edge on. In a Compose sheet, focus the field after the sheet opens, or the keyboard never shows | `expo-ui` |
| Number field | `keyboardType="ascii-capable-number-pad"` for Latin digits on Arabic phones | `number-pad`; normalise Arabic-Indic digits on input | |
| RTL | Wrap each Stack in `<LocaleDirContext.Provider value="rtl">` from `expo-router/react-navigation`: pushes come from the left, back swipe from the right edge. Don't force `I18nManager` globally | Same provider; check the push direction on the device | `expo-router` |
| Motion values | `Easing.bezier(0.32, 0.72, 0, 1)` and the prototype's durations, in the theme | Material curves and durations from the prototype's `ANDROID` block, in the theme | `expo-design-system` |
| Reduce Motion | Honour it: crossfades instead of moves (Reanimated's `useReducedMotion`) | Same | `expo-animation` |

## Lessons (each one cost a round trip)

- **"The iPhone feels native, Android feels patched."** That's the expected result when the prototype is an iPhone design and Android gets React Native imitations. The fix is never more imitation. Use Android's own pieces: predictive back, Material sheets, ripple, haptic constants, a real blur or an honest tinted surface, and Material bars.
- **Animate transforms, not layout.** A picture growing by animating `left/top/width/height` reflows every frame. It looked fine on the iPhone and dropped frames on a 120 Hz Android.
- **Bars follow the move.** If the status/navigation bar changes colour when the route changes, it snaps at the tap and lingers after the close. Change it with the animation's own timing.
- **Fix text width during a move.** A label whose width follows the shrinking box wraps from one line to two at the end of the animation. Give it the final width for the whole move.
- **`unstable_sheetFooter` didn't work.** Only the footer rose with the keyboard and it covered the field. A Material sheet on Android and the form sheet on iOS solved it.
- **CSS values don't translate 1:1.** A `backdrop-filter: blur(18px)` with 58% white became an opaque white button as `BlurView intensity={40}` with the same overlay. Tune on the phone against a side-by-side screenshot.
- **A new native dependency means a rebuild**, and in a project with decision records, a short ADR (`@expo/ui`, `expo-blur`, `react-native-keyboard-controller`).
- **Ask before changing a platform's look.** Swapping the iOS shrink for a ripple on Android, or a dialog for a sheet, changes what the user approved. Show it in the prototype's Android mode first.
