# ADR 0001 — Decisions live in docs; ADRs for load-bearing ones

- Status: Accepted ({{OWNER}}, {{DATE}})
- Date: {{DATE}}
- Deciders: {{OWNER}}

## Context

Work happens across many sessions, people and AI agents. A decision made in a conversation is
lost unless it is written where the next session reads first.

## Decision

`docs/decisions.md` lists every decision in one line. Load-bearing ones also get an ADR in
`docs/adr/`. `AGENTS.md` makes agents read both before working. A change that contradicts a
document updates it in the same commit.

## Alternatives considered

- Decisions only in chat or issue threads: not read by the next session.
- One long design document: goes stale; nobody knows which parts still hold.

## Consequences

- Every session starts from the same facts; re-litigating needs a new ADR.
- Docs are part of "done", which costs minutes per change.

## Enforcement / gates

The definition of done in `AGENTS.md` includes "docs updated in the same change".
