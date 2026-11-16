# Roadmap

**Owner:** {{OWNER}} · **Last updated:** {{DATE}}
**Goal:** {{GOAL}}

This file owns sequencing and the open work. The contracts live in the linked docs; why each
decision was made lives in [`adr/`](adr/).

## How we work

- **Ground up, one step at a time.** A step is done when its gate passes; the next step starts
  then. A failing gate is fixed and re-run, never averaged away.
- **No unnecessary complexity and no premature optimization.** Prefer deleting to abstracting;
  the smallest change that passes the gate.
- **The owner decides UI and UX.** Engineering shows options (an HTML prototype) and builds
  what the owner chooses.
- **Real devices decide native behaviour.** A simulator or a unit test is not a device test.
- **Docs change in the same commit as the code they describe.**

## What "working" means

In user terms, and measurable: {{WORKING}}

---

## Steps

### S0 — {{STEP}}

What it delivers, in two or three lines.

- **Gate:** the exact checks that must pass (commands, device runs, numbers).
- **Open:** what is still unknown.

### S1 — {{STEP}}

…

## Owner actions

Things only the owner can do (accounts, keys, devices, decisions).

| When | Action |
|---|---|
| S1 | {{ACTION}} |

## Risks

| Risk | Mitigation | Step |
|---|---|---|
| Scope creep | This file + AGENTS.md no-go list | all |

# Owner notes

Free-form notes from the owner. Agents read them and turn them into steps, decisions or
`later.md` items; they don't edit them.

-
