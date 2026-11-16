---
name: project-blueprint
description: Set up or reorganise a software project (especially an Expo app with a backend) the way a well-run project is organised and managed. An AGENTS.md that tells any AI agent what to read first, what's decided, the repo map, commands and rules. A docs/ folder that is the build contract (plan with gated steps, a one-page decision log, ADRs, product, architecture, testing, security, operations, later), research kept apart from decisions, a playground for HTML design work, official skills installed per project, every command in package.json, one CI gate, and docs updated in the same commit as the code. Use whenever the user starts a new project, asks to organise, clean up or document a repo, wants a roadmap, plan, decision log or ADRs, says agents keep losing context or re-deciding things, or asks to "set it up like" a project they liked.
---

# Project blueprint

A project stays fast when every session, human or AI, starts from the same written facts: what is decided, what's next, how to check it works. This blueprint is how a real app was run with many agent sessions a day without losing decisions or drifting. Everything lives in the repo, in plain Markdown, next to the code.

## The shape

```
AGENTS.md            how any agent works here: read order, decisions, map, commands, rules, done
CLAUDE.md            "@AGENTS.md" so Claude Code loads the same file
README.md            what it is, status, layout, run it locally
docs/                the build contract (if code and docs disagree, the code is wrong)
  README.md          index, conventions, ownership, the "change → update" table
  plan.md            the ONLY owner of sequencing: goal, how we work, gated steps, owner actions, risks, owner notes
  decisions.md       one line per decision (D1, D2, …), who decided and when
  adr/               why each load-bearing decision was made; superseded, never rewritten
  product.md         what a person sees and does, every state, the copy
  architecture.md    components, boundaries, flows, failure modes
  testing.md         layers L0–L6, commands, journeys, the last audit
  security.md · operations.md · later.md   (+ api.md, data-model.md, mobile.md, device-log.md when they exist)
research/            input, not decisions; one file per question
playground/          HTML prototypes: prototype.html is the approved visual source; archive/ for the rest
apps/ packages/ e2e/ the code, with one-way dependencies (reference/layout.md)
.agents/skills/      official skills, installed per project, linked into .claude/skills/
```

## Setting it up

1. **Read what exists first.** In an existing repo, read the README, any docs, `package.json`, the layout and recent git history. The blueprint organises what's there. It doesn't overwrite or invent.
2. **Show the plan to the user.** List which files you'll create, which you'll merge into, and the decisions you've found in their messages and the code. Then wait for an OK.
3. **Lay the files:** `bash <skill>/tools/scaffold.sh <repo> --name "App name" --owner "<how the user is referred to>"`. It never overwrites (an existing `.gitignore` only gets missing lines) and prints every placeholder left to fill.
4. **Fill the placeholders from evidence**: the conversation, the code, the user. Write real content, never "TBD". Delete sections that don't apply. A short true doc beats a long template.
5. **Record the decisions already made.** Each one gets a row in `decisions.md`. The load-bearing ones (vendor, data store, auth, main architecture, platform integration) also get an ADR.
6. **Write the plan as gated steps.** Each step says what it delivers and the exact gate (commands, device runs, numbers). Add owner actions (keys, accounts, devices, decisions only the user can make) and the risks.
7. **Commands in one place.** Every check, test and dev command is a `package.json` script, and AGENTS.md §4 lists them. CI runs the same gate (`lint && typecheck && test`, plus e2e as its own step).
8. **Install the official skills the project uses**, per project: `npx skills@latest add <source> -a universal claude-code -y -s <skills>`. List them in AGENTS.md §13 and refresh them with `npx skills@latest update -p`.

## Running it day to day

How a session, a decision, a step and a cleanup go is in [reference/how-we-work.md](reference/how-we-work.md). The short version:

- **Read order before work:** decisions → plan → the doc and ADR for the area.
- **The user decides scope, UI and UX.** When something is open, ask a multiple-choice question. Their answer becomes a `decisions.md` row the same day.
- **A change isn't done until the docs it contradicts are updated in the same commit** (the table in `docs/README.md`).
- **One step at a time.** A failing gate is fixed and re-run, never averaged away.
- **Owner notes** at the bottom of `plan.md` are the user's scratchpad. Agents turn them into steps, decisions or `later.md` items, and don't edit the notes.
- **House cleaning** is real work: dead code, stale docs, unused dependencies and skills, after each big change of direction.
- **Reports** for the user are a local HTML page (opened in the browser), not a wall of terminal text.

## Adapt, don't impose

Scale it to the project. A solo project pushing to main keeps the docs and gates but skips PR ceremony. A small tool may need only AGENTS.md, plan.md and decisions.md. Add a doc when its area exists, and ask before adding process the user didn't ask for.

Related skills: `expo-native-html-prototype` (the playground and the design process), `direct-real-phone-testing` (the `e2e/phone` lane and the device layer of testing.md).
