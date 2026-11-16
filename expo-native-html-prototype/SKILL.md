---
name: expo-native-html-prototype
description: Build a native iOS and Android app in Expo starting from a working HTML prototype. Quick design directions in one local HTML file, then one interactive phone prototype (real navigation, swipe and predictive back, sheets with the keyboard, a tile that grows into its screen, an iPhone/Android switch, options to compare one moment, slow motion, Reduce Motion, RTL, dark mode) that the user tries and decides on by feel. Then build each piece with the platform's own native component (Apple's on iPhone, Google's Material on Android) through Expo's official skills, carry the exact motion values over, and check the phone against the prototype. Use whenever the user wants to design or redesign app screens, explore UI directions, prototype transitions or animations, "see it in HTML first", turn a prototype or mockup into an Expo app, or complains that the app doesn't look or feel like the prototype or doesn't feel native on one platform.
---

# Build native apps in Expo from an HTML prototype

UI and UX are decided by feel, and feel needs something to touch. A local HTML prototype is the fastest thing that moves like an app: one file, no build, opened in a browser, changed in seconds. Once the user has picked everything in it, the Expo app is built to match, with **each platform's own components**, so the iPhone feels like an iPhone and the Android phone like an Android phone.

This skill is the process and the glue. How to build each native piece lives in the official skills below. Load them, because they're updated faster than this one.

## Official skills: load them, keep them fresh

| Skill | Source | Load it for |
|---|---|---|
| `expo-overview` | `expo/skills` | start of any Expo work: routes to the right skill, shared setup rules |
| `expo-native-ui` | `expo/skills` | native-feeling screens: HIG styling, semantic colours, native controls, blur |
| `expo-ui` | `expo/skills` | `@expo/ui`: real SwiftUI on iOS, Jetpack Compose on Android (sheets, pickers, menus) |
| `expo-router` | `expo/skills` | the native stack, modals, form sheets, headers, tabs |
| `expo-animation` | `expo/skills` | building motion right: UI thread, springs vs timing, gestures, haptics |
| `expo-design-system` | `expo/skills` | turning the prototype's tokens into the app's theme |
| `expo-project-structure` | `expo/skills` | laying out a **new** app |
| `edge-to-edge`, `navigation-event` | `android/skills` | Android system bars; predictive back |
| `swiftui-specialist` | Apple, ships with Xcode | when a piece is SwiftUI (`@expo/ui` or a native module) |
| `direct-real-phone-testing` | this repo | building, recording and measuring on the real phones |

```sh
npx skills@latest add expo/skills -a universal claude-code -y -s expo-overview expo-native-ui expo-ui expo-router expo-animation expo-design-system
npx skills@latest add android/skills -a universal claude-code -y -s edge-to-edge navigation-event
npx skills@latest update -p      # at the start of a session: refresh every project skill
```

Apple's skills ship inside Xcode, so copy them out again after each Xcode update (see `direct-real-phone-testing`). When an official skill disagrees with this one about an API, the official skill wins. Then fix this skill.

## The process

1. **Directions** (an hour, not a day). Put 3–5 genuinely different directions for the key screen side by side in **one local HTML file** at phone size, with real-looking content: ten items, long names, missing photos, an empty state. Add a few toggles (tone, density) if they help the user choose. Open it in the browser. Don't use a hosted canvas or a build step. → [reference/prototype.md](reference/prototype.md#directions)
2. **The prototype.** Start from [templates/prototype.html](templates/prototype.html). Make the chosen direction one working phone: every screen, every transition, the keyboard, sheets, back gestures. The side panel offers options only for moments still being decided (A/B/C for the same transition), plus platform, direction, theme, slow motion and Reduce Motion. → [reference/prototype.md](reference/prototype.md)
3. **The user decides by feel.** They try it and you change it. Ask multiple-choice questions when something is open. Once a choice is made, mark it ("Picked") or remove its option, record it in the project's decisions log, and archive rejected directions under `playground/archive/`. **The prototype is the spec.**
4. **Map every piece to a native component per platform** before writing code. Use [reference/native-mapping.md](reference/native-mapping.md). The look is shared, but the mechanics are each platform's own (sheets, back, press feedback, haptics, bars, blur). Write the plan down, and ask the user about anything that changes how a platform looks.
5. **Carry the motion values over exactly.** Curves and durations from the prototype's `IOS` / `ANDROID` blocks go into the app's theme, not retyped per screen.
6. **Check the phone against the prototype**, on both platforms: screenshots side by side, then recordings of every transition, judged against the platform's own apps. Issues often show only mid-transition. → [reference/fidelity-check.md](reference/fidelity-check.md)

## Rules that came from real feedback

- **No cramming, no clutter, one-handed.** Primary actions sit at the bottom, within thumb reach (a floating + at the bottom end, sheets that open low). Back and title share one line. Give everything room.
- **A tap acts once, on release.** No shrink on press followed by an expand on release: it feels broken. iOS dims while the finger is down. Android ripples.
- **Show transitions, not static states.** Options exist to compare moments in motion (how Add opens, how a name edit slides up). A panel full of state switchers hides the motion.
- **Design for both platforms from the start.** A prototype drawn as an iPhone becomes a perfect iPhone app and a patched Android app. Use the panel's Android mode to agree on Android's pieces (top bar, sheet, back, ripple) before building.
- **Don't reinvent platform components.** If the platform has it (sheet, back gesture, haptics, blur, top bar), use the native one. Hand-made imitations are where "feels off" comes from.
- **Every word and colour comes from one place** (strings file, theme tokens), in the prototype and in the app.
- **Real content and RTL from day one** when the app serves right-to-left users. Mirror positions with logical start/end, not left/right.

## What the template gives you

`templates/prototype.html` is a working, tested starting point, with sample content (trips) to replace:
- a native-like stack: iOS push with full-screen swipe back; Android shared-axis push with predictive back from either edge, or `Esc`;
- sheets that open with the keyboard, ride it, and drag down to close;
- a tile whose picture grows into its screen and shrinks back (with options to compare: grow / push / slide up);
- press feedback per platform, a frosted iOS + vs a Material FAB, top bars per platform;
- a panel with iPhone/Android, English/Arabic (RTL), light/dark, slow motion ×5 and Reduce Motion, remembered per viewer.

`tools/shoot.mjs` walks the prototype in headless Chrome and saves phone screenshots, for side-by-side checks and for catching mid-transition frames.
