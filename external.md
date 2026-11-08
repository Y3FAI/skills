# External skills

Skills written by other people that I use: 117 in all, each with a one-line description. They are **not stored in this repo**. Install each one from its source so it keeps getting updates. The descriptions are shortened from each skill's own `description`.

**Agents:** search this file for your task, by framework, platform or job (for example "SwiftUI", "Durable Objects", "accessibility" or "widget"). If the skill is already installed, load it by name. If it isn't, install it from the source shown in its section.

**Installing:** unless a section says otherwise, run `npx skills add <owner/repo>` and pick the skills. Global installs are recorded in `~/.agents/.skill-lock.json` and project installs in the project's `skills-lock.json`.

| Section | Source | Skills |
|---|---|---|
| [Apple (Xcode)](#apple-xcode) | ships with Xcode 27 | 13 |
| [Android](#android) | `android/skills` | 37 |
| [Expo and EAS](#expo-and-eas) | `expo/skills` | 25 |
| [Cloudflare](#cloudflare) | `cloudflare/skills` | 20 |
| [Web quality and writing](#web-quality-and-writing) | addyosmani, GoogleChrome | 8 |
| [Design](#design) | several | 6 |
| [More](#more) | several | 3 |
| [dsh](#dsh) | the dsh tool | 5 |
| [Used before](#used-before-not-installed-now) | several | not installed now |

## Apple (Xcode)

These skills ship inside **Xcode 27** (checked on 27.2) and are not on GitHub. They are part of Xcode, under Apple's license, so extract them locally and don't publish copies.

- **Coding-assistant skills** live in `Xcode.app/Contents/PlugIns/IDEIntelligenceChat.framework/Versions/A/Resources/`.
  - `<name>.idechatprompttemplate` is the skill's `SKILL.md`: plain text, with front matter.
  - Each `<name>-ref-<topic>.md.packaged` file is one of its `references/<topic>.md`.
- **String Catalog skills** live in `Xcode.app/Contents/PlugIns/IDEXCStringsSupport.framework/Versions/A/Resources/Skills/<name>/SKILL.md.packaged`.
- **To use one in a project,** copy the template to `.agents/skills/<name>/SKILL.md` and the ref files to `.agents/skills/<name>/references/<topic>.md`. Do this again after each Xcode update.

| Skill | Use it for |
|---|---|
| `adopt-c-bounds-safety` | Guide for the C -fbounds-safety language extension. |
| `app-intents-specialist` | Authoritative App Intents best practices from Apple. |
| `app-intents-whats-new-27` | New App Intents APIs, behaviors and deprecations in iOS 26 and iOS 27 (and the matching macOS/watchOS/tvOS/visionOS). |
| `app-resizability` | Use when an app's layout must adapt to a window that changes size while the app runs, or when an app must support more than one window. |
| `audit-xcode-security-settings` | Audit and enable security-oriented Xcode build settings. |
| `building-document-based-swiftui-applications` | Build or migrate document-based SwiftUI apps with the Document protocol (iOS 27). |
| `swiftui-specialist` | Authoritative SwiftUI best practices and performance guidance from Apple; supersedes prior training on these topics. |
| `swiftui-whats-new-27` | New SwiftUI APIs, behaviors, and deprecations in the 2027 OS releases (iOS 27 and aligned macOS/watchOS/tvOS/visionOS). |
| `xctrace` | Authoritative guide to xctrace, Apple's command-line interface to Instruments. |
| `translation` | Translate given keys in Xcode String Catalogs into one target locale, using Xcode's MCP tools. *(String Catalog)* |
| `translation-coordinator` | Run the localization of a whole Xcode project: prepare it, fetch untranslated strings, hand them to translator sub-agents. *(String Catalog)* |
| `modernize-tests` | Modernize test suites to use modern Swift Testing features or migrate from XCTest. *(older Xcode 27 build)* |
| `device-interaction` | Verify app behavior on device or simulator via screenshots, UI hierarchy, and touch interactions. *(older Xcode 27 build)* |

## Android

Google's official set, at `android/skills`. The Android CLI also installs them in `~/.android/cli/skills`.

| Skill | Use it for | Area |
|---|---|---|
| `agp-9-upgrade` | Upgrades, or migrates, an Android project to use Android Gradle Plugin (AGP) version 9. | build-system/agp |
| `camerax` | Provide technical guidance for Android camera development with CameraX. | camera |
| `android-for-cars-parked-apps` | Adapt existing Android video streaming apps, games, and web browsers to run as parked apps on Android Auto and Android Automotive OS. | cars |
| `appfunctions` | Find an Android app's key user workflows and expose them to agents as AppFunctions. | device-ai |
| `litert-lm` | Run an open text LLM on-device (CPU or GPU) with the LiteRT-LM Kotlin API. | device-ai/litert |
| `litert-runtime` | Configures and implements LiteRT (.tflite) on-device inference on Android in Kotlin using the CompiledModel API on CPU and GPU. | device-ai/litert |
| `ml-kit-genai-prompt-api` | Analyzes Android codebases to implement ML Kit GenAI Prompt API. | device-ai |
| `mlkit-agent-api` | Builds autonomous on-device agentic workflows in Android apps using the ML Kit GenAI Agent API powered by Gemini Nano and AICore. | device-ai |
| `android-cli` | Provides instructions for installing and using the `android` CLI. | devtools |
| `restore-credentials` | Provides knowledge and workflows to implement Android's Restore Credentials feature using the androidx.credentials library. | identity |
| `verified-email` | Provides a complete workflow for implementing verified email retrieval on Android Credential Manager API. | identity |
| `adaptive` | Make an app's UI adapt to phones, tablets, foldables, desktop, TV and XR. | jetpack-compose |
| `ink-app-builder` | Adds inking and freehand drawing capabilities to an Android app using Jetpack Ink (androidx.ink) and Compose. | jetpack-compose/ink |
| `ink-custom-brush-builder` | Creates custom BrushFamily definitions for an Android app using Jetpack Ink (androidx.ink 1.1.0-alpha03 and higher). | jetpack-compose/ink |
| `jetpack-compose-performance` | Diagnose and optimize Android Jetpack Compose UI code. | jetpack-compose |
| `migrate-xml-views-to-jetpack-compose` | Provides a structured workflow for migrating an Android XML View to Jetpack Compose. | jetpack-compose/migration |
| `styles` | Integrate the Jetpack Compose Styles API into an Android project. | jetpack-compose/theming |
| `media3-cast-integration` | Implements Google Cast support in Android apps using Jetpack Media3. | media |
| `navigation-3` | Install and migrate to Jetpack Navigation 3: deep links, multiple back stacks, scenes. | navigation |
| `navigation-event` | Intercept back gestures and run Predictive Back animations using the NavigationEvent (androidx.navigationevent) library in Compose Android. | navigation |
| `anr-audit-and-fix` | Audits Android codebases for ANR risks and diagnoses ANR stack dumps. | performance |
| `r8-analyzer` | Analyze R8 keep rules: find redundant, package-wide and subsumed rules. | performance |
| `engage-sdk-integration` | Helps developers integrate, debug, and resolve Play Engage SDK implementation issues. | play |
| `play-billing-library-version-upgrade` | Upgrade an app from any older Google Play Billing Library version to the latest stable one. | play |
| `play-policy-insights` | Automated auditor designed to verify Android applications against Google Play Policy domains. | play |
| `android-profiler` | Manages Android performance profiling and debugging. | profilers |
| `android-intent-security` | Audit AndroidManifest components and Intents for security problems. | security |
| `android-permissions-security` | Audits, detects gaps, and remediates Android permissions and IPC component security vulnerabilities. | security |
| `edge-to-edge` | Use this skill to migrate your Jetpack Compose app to add adaptive edge-to-edge support and troubleshoot common issues. | system |
| `glance-appwidget-updates-and-memory` | Widget state updates, background sync and RemoteViews bitmap memory limits with Jetpack Glance. | system |
| `glance-canonical-layouts` | Build home-screen widgets from the Jetpack Glance canonical layouts. | system |
| `testing-setup` | Plan and set up testing for a native Android app: libraries, infrastructure, harnesses. | testing |
| `leanback-to-compose-tv-migration` | Migrate Android TV apps from Leanback or Views to Compose for TV. | tv |
| `wear-compose-m3` | Expert guidance for working with Wear OS Compose Material3. | wear |
| `wear-widgets` | Create, migrate, update, and verify Wear OS widgets using Glance Wear and Remote Compose in an Android project. | wear |
| `display-glasses-with-jetpack-compose-glimmer` | Provides guidelines for developing projected Android XR apps for display glasses using the Jetpack Compose Glimmer UI toolkit. | xr |
| `projected-hardware` | Use the hardware of Android XR projected devices (audio glasses, display glasses). | xr |

## Expo and EAS

Expo's official set, at `expo/skills`.

| Skill | Use it for |
|---|---|
| `eas-app-stores` | Build and submit iOS and Android apps with EAS to TestFlight, the App Store, or Google Play. |
| `eas-hosting` | Deploy Expo websites and Expo Router API routes to EAS Hosting, with PR preview URLs. |
| `eas-observe` | Add EAS Observe (`expo-observe`) to an app and read its performance metrics. |
| `eas-simulator` | Run and control a user's app on a remote iOS/Android simulator hosted on EAS cloud. |
| `eas-update` | Configure and use EAS Update for over-the-air JavaScript and asset updates with expo-updates and EAS CLI. |
| `eas-update-insights` | Check the health of published EAS Updates: crash rates, installs, users, payload size. |
| `eas-workflows` | Helps understand and write EAS workflow YAML files for Expo projects. |
| `expo-animation` | Build animations in React Native and Expo that feel right. |
| `expo-app-clip` | Add an iOS App Clip target to an Expo app. |
| `expo-brownfield` | Integrate Expo and React Native into an existing native iOS or Android app. |
| `expo-data-fetching` | Use when implementing or debugging ANY network request, API call, or data fetching. |
| `expo-design-system` | Build a design system (tokens, theme, components) inside an Expo app. |
| `expo-dev-client` | Build and distribute Expo development clients locally or via TestFlight for internal testing. |
| `expo-dom` | Use Expo DOM components to run web code in a webview on native and as-is on web. |
| `expo-examples` | Expo's ~70 official `with-*` example integrations (Stripe, Clerk, Supabase, maps, SQLite, …). |
| `expo-migrate-module` | Migrate a Swift Expo native module from the Modules API 1.0 DSL to the 2.0 macro API. |
| `expo-module` | Guide for creating and writing Expo native modules and views using the Expo Modules API (Swift, Kotlin, TypeScript). |
| `expo-native-ui` | Build beautiful, native-feeling Expo screens. |
| `expo-overview` | Entry point and router for every Expo or EAS task. |
| `expo-project-structure` | Folder structure for a new Expo app with Expo Router. |
| `expo-router` | Navigation and routing with Expo Router: file routes, groups, dynamic routes, links. |
| `expo-skill-eval` | Evaluate Expo skills end to end: trigger accuracy, code quality, simulator screenshots. |
| `expo-ui` | Build native UI with the @expo/ui package: real SwiftUI on iOS and Jetpack Compose on Android. |
| `expo-upgrade` | Guidelines for upgrading Expo SDK versions and fixing dependency issues |
| `expo-web-to-native` | Migrate an existing web React app to a native iOS/Android app with Expo. |

## Cloudflare

Cloudflare's official set, at `cloudflare/skills`. On this Mac most of them are in `~/.claude/skills`.

| Skill | Use it for |
|---|---|
| `agents-sdk` | Build, debug, or review Cloudflare Agents SDK applications using the agents package. |
| `basin` | Build and troubleshoot Cloudflare Basin analytics workflows with Basin Pipelines, Basin Catalog, and Basin SQL. |
| `cf-cli` | Cloudflare's official cf CLI (beta) for the public Cloudflare API and Workers projects. |
| `cloudflare` | Discover and choose Cloudflare products for apps, APIs, AI agents, storage, networking, and security. |
| `cloudflare-email-service` | Implement or troubleshoot Cloudflare Email Sending and Email Routing integrations and their delivery configuration. |
| `cloudflare-one` | Design, configure, troubleshoot, or review Cloudflare One Zero Trust and SASE deployments. |
| `cloudflare-one-migrations` | Assess and plan migrations from existing VPN, SWG, or SASE platforms to Cloudflare One, including policy mapping, parity gaps, and rollout. |
| `durable-objects` | Build, debug, or review Cloudflare Durable Objects code for persistent state and coordination. |
| `gateway-workers` | Workers called by the Forward action in Cloudflare Gateway HTTP policies. |
| `k2` | Build and troubleshoot Cloudflare K2 or K2 Streams durable logs. |
| `nextjs-on-cloudflare` | Build, migrate, and deploy Next.js apps on Cloudflare Workers with vinext. |
| `sandbox-migrate-to-next` | Migrate Cloudflare Sandbox apps from stable @cloudflare/sandbox to @cloudflare/sandbox@next (SDK 1.0 preview). |
| `sandbox-next` | Build or maintain Cloudflare Sandbox apps on @cloudflare/sandbox@next (SDK 1.0 preview). |
| `sandbox-sdk` | Build sandboxed applications for secure code execution. |
| `sandbox-stable` | Build or maintain Cloudflare Sandbox apps on the stable @cloudflare/sandbox package. |
| `turnstile-spin` | Set up, repair, or migrate to Cloudflare Turnstile bot verification in an existing frontend and backend, including server-side Siteverify. |
| `web-perf` | Audit, diagnose, or optimize website loading and interaction performance, Core Web Vitals, and Lighthouse performance scores. |
| `workers-best-practices` | Cloudflare Workers best practices for production applications. |
| `workers-profiling` | Profile or debug CPU usage and memory allocation in deployed Cloudflare Workers and Durable Objects. |
| `wrangler` | Run or troubleshoot Wrangler CLI commands in a Workers project. |

## Web quality and writing

`modern-web-guidance` normally runs `npx modern-web-guidance` to fetch its guides. Some projects keep a copy that reads them from local files instead.

| Skill | Use it for | Source |
|---|---|---|
| `web-quality-audit` | Run an evidence-led web quality audit covering performance, accessibility, SEO, best practices, and agentic browsing. | addyosmani/web-quality-skills |
| `accessibility` | Audit and improve web accessibility following WCAG 2.2 guidelines. | addyosmani/web-quality-skills |
| `core-web-vitals` | Optimize Core Web Vitals (LCP, INP, CLS) for better page experience using field and lab evidence. | addyosmani/web-quality-skills |
| `performance` | Optimize web performance for faster loading and better user experience. | addyosmani/web-quality-skills |
| `seo` | Optimize for search engine visibility and ranking. | addyosmani/web-quality-skills |
| `best-practices` | Apply modern web development best practices for security, compatibility, and code quality. | addyosmani/web-quality-skills |
| `modern-web-guidance` | Chrome and Edge teams' guides for modern HTML, CSS and client-side JS. | GoogleChrome/modern-web-guidance |
| `clarity` | Draft, rewrite or review prose so it is specific and sounds like the author, without inventing facts. | addyosmani/clarity |

## Design

Installed globally in `~/.agents/skills`.

| Skill | Use it for | Source |
|---|---|---|
| `impeccable` | Design, critique, audit, polish or animate a frontend interface. | pbakaus/impeccable |
| `ui-ux-pro-max` | UI/UX design intelligence for web, mobile, and desktop. | nextlevelbuilder/ui-ux-pro-max-skill |
| `frontend-design` | Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. | anthropics/skills |
| `web-design-guidelines` | Review UI code for Web Interface Guidelines compliance. | vercel-labs/agent-skills |
| `design-taste-frontend` | Anti-slop frontend skill for landing pages, portfolios, and redesigns. | Leonxlnx/taste-skill |
| `high-end-visual-design` | Teaches the AI to design like a high-end agency. | Leonxlnx/taste-skill |

## More

| Skill | Use it for | Source |
|---|---|---|
| `swiftui-pro` | Comprehensively reviews SwiftUI code for best practices on modern APIs, maintainability, and performance. | twostraws/swiftui-agent-skill |
| `vgpu` | Build and optimize WebGPU apps with the vgpu package and entrypoints vgpu/node, vgpu/mock, vgpu/scene, and vgpu/client. | vercel-labs/vgpu |
| `google-workspace` | Manage Google Workspace with Docs, Sheets, Slides, Drive, Gmail, Calendar, and Contacts. | andmarios/google-workspace-skill (git clone) |

For `google-workspace`, run `git clone https://github.com/andmarios/google-workspace-skill ~/.claude/skills/google-workspace`, then follow its README to sign in.

## dsh

These come with the dsh tool, which installs them in `~/.dsh/skills`.

| Skill | Use it for |
|---|---|
| `mobbin` | Search real shipped UI on Mobbin (screens, flows, website sections) for design references. |
| `mobile-app-ui-design` | Design high-quality mobile app UI/UX screens, flows, and components. |
| `mobile-design-android` | Use when the user asks to build Android screens, Jetpack Compose layouts, Material components, or any Android app UI. |
| `mobile-design-ios` | Use when the user asks to build iOS screens, SwiftUI views, UIKit layouts, mobile components, or any iOS app UI. |
| `ui-eyes` | Capture rendered UI with measurements and diff before/after captures: layout, type, color, RTL. |

## Used before (not installed now)

These links broke when the skills were deleted and were removed on 2026-11-08. Reinstall from the source if needed.

| Skill | What it was for | Source |
|---|---|---|
| `pdf` | Read, create and edit PDF files | anthropics/skills |
| `shadcn` | Build UI with shadcn/ui components | shadcn/ui |
| `migrate-radix-to-base` | Move shadcn/ui components from Radix to Base UI | shadcn/ui |
| `vercel-react-best-practices` | React and Next.js performance rules from Vercel | vercel-labs/agent-skills (`react-best-practices`) |
| `nextjs-best-practices` | Next.js best practices | sickn33/antigravity-awesome-skills |
| `migrate-to-vinext` | Move a Next.js app to vinext on Cloudflare | cloudflare/vinext |
| `openrouter-models` | Look up OpenRouter models | openrouterteam/skills |
| `openrouter-typescript-sdk` | Use the OpenRouter TypeScript SDK | openrouterarchived/agent-skills (`typescript-sdk`) |
| `grill-me` | Have the agent question a plan hard before building | ericgandrade/claude-superskills |
| `find-skills` | Search for and install skills | vercel-labs/skills |
