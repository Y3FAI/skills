# AGENTS.md — {{PROJECT}}

You are working on **{{PROJECT}}**: {{ONE_LINE}}

**Current status:** {{STATUS}}. The roadmap, and the only source of sequencing and open work, is
[`docs/plan.md`](docs/plan.md). Do not invent scope or start a second architecture.

---

## 1. Read before doing anything

In this order:

1. [`docs/decisions.md`](docs/decisions.md): frozen decisions.
2. [`docs/plan.md`](docs/plan.md): the roadmap, with steps, gates, open work and owner actions.
3. [`docs/product.md`](docs/product.md): screens, flows, copy, edge states.
4. [`docs/architecture.md`](docs/architecture.md): components, boundaries, flows.
5. [`docs/testing.md`](docs/testing.md): what must be tested and how.
6. [`docs/security.md`](docs/security.md): non-negotiable security rules.
7. The ADR that owns the area you are changing (`docs/adr/`).

If a task conflicts with those docs, stop and resolve the conflict before coding. A change that
makes a document false is incomplete.

## 2. Decisions that are already made

Don't re-litigate these without the owner. Keep this list short. The full log is
`docs/decisions.md`.

- {{DECISION_1}}
- {{DECISION_2}}

If you believe a decision is wrong, write a short ADR proposal with evidence and wait. Don't
quietly implement an alternative.

## 3. Repository map

```
{{LAYOUT}}
```

Dependency direction is one-way (write it down, then enforce it):

```
{{DEPENDENCIES}}
```

## 4. Commands

```bash
{{COMMANDS}}
```

If a command is not in `package.json` (or the project's task runner), add it there. Don't invent
one-off shell invocations that CI cannot run.

## 5. Architecture rules

- Routes and screens are thin; rules live in services and features.
- One owner per piece of state; one network layer; one source of truth per contract.
- {{RULE}}

## 6. Security rules

- Never commit secrets; never print them (key names only).
- Never log personal data, codes or tokens.
- Every endpoint: auth + authz + rate limit + validation + test.
- {{RULE}}

## 7. UI rules

- The approved visual source is `playground/prototype.html`. The owner decides UI and UX.
- Every word comes from the strings file; every colour, size and motion value from the theme.
- Every data screen has loading, error, empty and content states. No empty flash.
- {{RULE}}

## 8. Testing rules

- Every behaviour that can break gets a test at the lowest layer that can prove it.
- Real devices decide native behaviour: a simulator or a unit test isn't a device test.
- No arbitrary sleeps; wait for the event.
- {{RULE}}

## 9. Docs and decisions

- A change is not done until the docs it contradicts are updated **in the same change**.
- The table in `docs/README.md` says which doc each kind of change updates.
- New load-bearing dependency or vendor → ADR.
- Don't edit an accepted ADR to reverse it; add a new ADR that supersedes it.

## 10. Working with subagents

Use them for independent second opinions: architecture or ADR review before a risky step,
security review, test-plan review, a second look at a risky diff. Give them file paths and the
exact question; they read the docs, not your summary. Record material findings in the relevant
doc or ADR. You own the result.

## 11. No-go list

Don't add without a new explicit owner decision:

- {{NO_GO}}

## 12. Definition of done

- [ ] behaviour and error states implemented;
- [ ] tests added or updated at the right layer;
- [ ] security checked (authz, limits, no secrets or personal data in code or logs);
- [ ] UI: loading/error/empty/content, accessibility, RTL and large text checked;
- [ ] docs updated in the same change;
- [ ] the gate is green: `{{GATE}}`;
- [ ] native or device behaviour verified on a real device, or marked blocked with the reason.

## 13. Installed skills

Official skills live in `.agents/skills/` (linked into `.claude/skills/`), installed per
project, only the ones this project uses. Load the relevant skill before a task in its domain.
They are guidance, not a substitute for the decisions in `docs/`.

- {{SKILLS}}
