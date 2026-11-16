# Testing strategy

**Last updated:** {{DATE}}

## 1. What we are protecting

The few things that must never break, in user terms.

## 2. Principles

- Test each behaviour at the lowest layer that can prove it.
- Fakes are first-class (fake clock, fake vendors); no real third-party services in CI.
- No arbitrary sleeps; wait for events.
- Real devices decide native behaviour; never a simulator for the final word.

## 3. The layers

| Layer | What | Command | In the gate? |
|---|---|---|---|
| L0 | static: lint, types, contracts | `{{CMD}}` | yes |
| L1 | pure unit | `{{CMD}}` | yes |
| L2 | component and screen logic | `{{CMD}}` | yes |
| L3 | integration against real local services | `{{CMD}}` | yes |
| L4 | end to end through real processes | `{{CMD}}` | separate gate |
| L6 | the real phone (journeys, recordings, timings) | `{{CMD}}` | before a release |

## 4. Journeys

J1 first run · J2 the core action · J3 relaunch · J4 failure and recovery · J5 settings.

## 5. Current audit

What was last run, when, with what result; defects found and fixed.
