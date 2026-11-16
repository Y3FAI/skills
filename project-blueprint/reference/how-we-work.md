# How we work

The routines that keep the blueprint true. Each exists because its absence cost real time.

## A session

1. Read `docs/decisions.md`, `docs/plan.md` (where we are and what's next), then the doc and ADR for the area you'll touch. Read the docs themselves, not a summary.
2. Do the smallest change that moves the current step toward its gate.
3. Run the gate (`lint && typecheck && test`, plus the step's own checks: e2e, device runs).
4. Update the docs the change contradicts, in the same commit.
5. Commit in logical pieces with plain messages that say what changed and why.
6. Tell the user what changed, what was verified and how, and what's left. Say "not verified" where it's true.

## A decision

- In conversation: the user answers ("phone numbers only", "no dark mode", "option C"). Add a `decisions.md` row the same day: the decision in bold, who and when (`owner, 2026-11-15`), and what it means in practice.
- Load-bearing (a vendor, data store, auth, the main architecture, a platform integration, an expensive-to-reverse choice): also write an ADR. Context with the user's own words, the decision as numbered points, alternatives with why not, consequences, and how it's enforced.
- Changing a decision: a new row or a new ADR that says what it supersedes. Mark the old ADR `Superseded by NNNN`. Never rewrite history.
- An agent that thinks a decision is wrong writes an ADR **proposal** with evidence and waits. It doesn't implement the alternative quietly.

## A step

- Steps are numbered (S0, S1, …) and gated, not dated: "done" means the gate passed, not that a week went by.
- A step entry: what it delivers (2–3 lines), the **gate** (exact commands, device runs, numbers), what's open. When done: ✅ with the date and the evidence (test counts, run results).
- Big direction changes get their own section (e.g. "Road to production" with phases), written from evidence such as device runs, benchmarks and a review.
- The user's actions (keys, accounts, devices, decisions) sit in one table, so the work never waits silently on them.

## What "working" means

Write it once, in user terms, measurable, at the top of the plan (e.g. "20 consecutive answered calls, both directions, two-way audio for 60 s"). Latency targets go next to it, but speed never waives a functional failure. Reliability comes first: a fast UI can hide a wait, but it can't hide a failure.

## Research

- Research goes in `research/`, one file per question: the question, the date, the sources, and what it means here.
- It isn't a decision until it lands in `decisions.md` or an ADR.
- Delete research that a later decision made obsolete. Git keeps it.

## House cleaning

After a change of direction (a vendor dropped, a redesign), run a cleanup pass as its own step. Remove the dead code, dependencies, config, tests, docs, research and skills of the old path, and rewrite the docs to match the code. The gate is green tests, and a search for the old names that comes back empty.

## Reviews

For risky moments (architecture before a big step, security of auth or uploads, a test plan, a large diff), ask an independent reviewer (a subagent or advisor) with file paths and the exact question. Record what it finds in the doc or ADR. The decision stays with the user and you.

## Reports

When the user asks what happened (an overnight test run, an audit), write a local HTML page: summary first, then evidence (tables, screenshots, logs), then what's left and what needs them. Open it in the browser. Keep it out of the repo unless they want it kept.

## Secrets and personal data

- `.env*` is gitignored; `.env.example` lists names only. Never print a secret: list key names.
- Never log phone numbers, codes, tokens or message contents. Test data is fake.
- A public repo (a skills repo, an open-source app) gets a scan for IDs, keys, emails and names before every push.
