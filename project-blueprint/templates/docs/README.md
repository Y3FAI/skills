# {{PROJECT}} docs

This folder is the build contract. Research is input; decisions are here. If a document and the
code disagree, the code is wrong until the document is deliberately changed.

| Document | Answers | Audience |
|---|---|---|
| [plan.md](plan.md) | What are we building, in what order, and when is it done? | owner, AI agent |
| [decisions.md](decisions.md) | What is frozen? | owner, everyone |
| [product.md](product.md) | What does a person see and do? | design, mobile, QA |
| [architecture.md](architecture.md) | What are the components, boundaries and flows? | engineering, AI agent |
| [testing.md](testing.md) | What tests exist, at which layer, and what must pass? | everyone |
| [security.md](security.md) | What are the threats and the rules? | everyone |
| [operations.md](operations.md) | How do we run, deploy, observe and recover it? | engineering, owner |
| [later.md](later.md) | What is deliberately not now? | owner |
| [adr/](adr/) | Why each load-bearing decision was made | everyone |

Add a document when its area exists, not before: `api.md` (the HTTP/WebSocket contract),
`data-model.md` (what data lives where), `mobile.md` (app structure, design system, screens),
`device-log.md` (what happened on real phones).

## Conventions

- **MUST / MUST NOT**: a rule. Changing it needs an ADR and the owner's approval.
- **SHOULD**: the default. Deviate with a reason in the commit and a note in the nearest doc.
- **MAY**: optional.
- Diagrams are Mermaid; tables are plain Markdown. Dates are ISO 8601 (2026-11-16).
- Write plainly: short sentences, the reason next to the rule.

## Ownership

`plan.md` is the only document that owns sequencing: other docs link to it instead of carrying
their own phase plans. `decisions.md` is the one-page answer to "what did we decide?"; the ADRs
hold the reasoning.

## Keeping docs current

A change is not done until the docs it contradicts are updated in the same change:

| Change | Update |
|---|---|
| New or changed endpoint / event | `api.md`, the contract package, tests |
| New table, column or index | `data-model.md`, a migration |
| New screen or route | `mobile.md`, `product.md`, the device journeys |
| New design token or component | `mobile.md` |
| New step or scope cut | `plan.md`, `later.md` |
| New load-bearing dependency or vendor | an ADR |
| New environment variable or secret | `operations.md`, `.env.example`, `security.md` |
| A decision made in conversation | `decisions.md` (and an ADR if it is load-bearing) |

`AGENTS.md` at the repository root tells an AI agent how to apply these rules.
