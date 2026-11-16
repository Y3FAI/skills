# Repository layout

## An Expo app with a backend (pnpm monorepo)

```
apps/
  mobile/              Expo app: src/app (routes only), src/screens, src/features, src/lib, src/theme, src/strings.json
  api/                 the backend (e.g. one Cloudflare Worker: routes → services → stores)
packages/
  contracts/           the wire contract (Zod schemas + inferred types), imported by both apps
  config/              shared tsconfig / ESLint / Prettier
e2e/
  api/                 real backend process + HTTP/WebSocket tests
  phone/               the real-phone lane (direct-real-phone-testing)
docs/ research/ playground/   (see SKILL.md)
patches/               pnpm patches for third-party fixes, each explained in an ADR or a comment
```

Root files: `package.json` (all scripts, `packageManager`, `engines`), `pnpm-workspace.yaml` (`apps/*`, `packages/*`, `e2e/*`), `tsconfig.base.json`, `.editorconfig`, `.gitignore`, `skills-lock.json`, `AGENTS.md`, `CLAUDE.md`, `README.md`.

## Dependency rules (write them in AGENTS.md §3)

```
apps/mobile → packages/contracts
apps/api    → packages/contracts
e2e         → apps (through real processes, not source imports)
packages/*  → packages/config
```

- Apps never import each other. Server-only code never enters the mobile bundle.
- The contract package imports no app, framework, database or native code.
- Change the contract first, then the API, then the app, then the docs.
- Expo Router's `src/app` holds routes only. Screens compose features and primitives.
- One network layer (the API client). One owner per piece of live state. No `fetch` in screens.
- Every colour, size and motion value comes from the theme. Every word comes from the strings file, and a test can enforce "no literal UI text in code".

## Scripts (examples)

```
dev:api · dev:mobile · seed
lint · typecheck · test (fast lanes) · test:e2e:local (real processes) · test:native
phone:build · phone:runner · phone:test · phone:smooth · phone:android
```

One gate for every change (`pnpm lint && pnpm typecheck && pnpm test`), which CI runs too, plus the e2e suite as its own step. A command that isn't a script doesn't exist: CI can't run it and the next session won't find it.

## Smaller projects

Keep the ideas, not the folders: one `src/`, `docs/` with plan + decisions (+ ADRs when something load-bearing is chosen), `AGENTS.md`, scripts in `package.json`. Grow into the monorepo only when a second app or a shared contract appears.
