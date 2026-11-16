# Architecture Decision Records

ADRs are short, durable records of load-bearing choices. An accepted ADR is not edited to
reverse it; a new ADR supersedes it. Status values: `Proposed`, `Accepted`, `Superseded`,
`Rejected`.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-record-decisions.md) | Decisions live in docs; ADRs for load-bearing ones | Accepted ({{DATE}}) |

## When to write an ADR

- A new vendor or platform dependency.
- A change to auth, data stores, the main architecture or a platform integration.
- A choice that would be expensive to reverse.
- A scope decision that removes a promised feature.

## Template

```
# ADR NNNN — Title
- Status: Proposed | Accepted (owner, date) | Superseded by NNNN
- Date:
- Deciders:
- Related:

## Context
## Decision
## Alternatives considered
## Consequences
## Enforcement / gates
```
