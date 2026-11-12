# The clarity check: no unclear, incoherent or incomplete explanation reaches the student

The student asked for this when the IT241 final guide was started (2026-11-09): "check is explanation clear and
coherent and full not having gaps". The reference implementation is `2026-fall/it241/final-prep/` in
github.com/Y3FAI/y3f: `build.py` and `src/clarity/README.md`. Reuse the idea, and adapt the checks to the course.

## Layer 1 · build checks (cheap, run on every build)
They caught real gaps in the first module built with them: 40 problems in Module 6.

| Check | How | What it caught |
|---|---|---|
| The answer is taught | The correct option's content words must be on the cards up to that section (≥ 60 %). An explanation with worked steps counts as teaching. | "ostrich algorithm" and "definitely" were missing from the cards; a semaphore question needed a sentence the card lacked |
| The explanation states the answer | The explanation must share at least 3 (or half) of the correct option's content words. | quote-only explanations that never named the answer; "None" answers explained without saying "none" |
| Written answers are full | "Name three …" needs ≥ 3 points; "differentiate" or "compare" needs both sides. | |
| Slide questions are answered | A slide line ending in "?" must be on the card with an answer right after it. | "Can request (3,3,0) by P4 be granted?" left open on the slides |
| Abbreviations | Spelled out at first use, unless whitelisted. | |
| No TeX on cards; no "section N", "the slide" or "the figure" | regex | |
| HTML appropriate structure for understanding | Flags a card table that should be another shape (rules below). The review judges the rest of the shape. | 19 tables in IT241 Module 6 and 22 in Module 9; Module 10 went from 25 tables to 9 (2026-11-11) |

Word matching needs a light stemmer: box/boxes, process/processes, ignore/ignoring, state/states.

### The structure check, rule by rule
The student asked for it by name: "HTML appropriate structure for understanding" (IT241 final, 2026-11-11). Too many
tables made the cards hard to read, and most of them were lists in disguise. For every table on a card (code blocks aside):

- **Under 2 body rows:** bullets. One row compares nothing.
- **A first column headed Step, Stage or Order, with wordy cells** (3+ words on average): a numbered list. A numeric trace (a disk-head schedule, a page-replacement run) stays a table.
- **Rows numbered 1., 2., …:** a numbered list. The numbers already make it one.
- **A cell over 12 words** (numbers and addresses don't count): shorten the cells and put the details in bullets under the table.
- **Two columns whose second averages over 7 words:** a term list (`Term :: meaning`). It's a glossary, not a comparison.
- **Two columns and under 6 rows of words:** a term list or bullets. Too small to need a grid.

What stays a table: a genuine side-by-side comparison with short cells (polling vs interrupts vs DMA), or data the
slide itself shows as a table (a port map, a vector table, device speeds, a worked trace). The IT241 code is
`structure()` in `final-prep/build.py`, about 30 lines; port it, and retune the thresholds if another course's cards
are written differently.

## Layer 2 · the clarity review (a gate)
1. The build writes a **pack**: per section, the slides' text, the card, and every question with its key and its explanation or model answer.
2. A reviewer **who did not write the section** reads it as a student, answers every question from the cards alone, then compares with the key. A fresh agent works; so does the student.
3. Rubric: **clear**, **coherent**, **complete** (no term before its definition, no missing algorithm step, no skipped step in a worked example, no dropped slide line), **answerable**, **explanations** (why the key is right; the tempting option on tricky items; model answers worth full marks), **correct** (recompute every number), **minimal**.
4. Verdicts go to `clarity/mNN.json` as `{section: {hash, verdict, issues}}`. The build refuses to write the page until every section passes **with the current hash**. `--draft` writes it anyway, so the page can be looked at while the review is pending.
5. Fix the issues, then re-review only the sections whose hash changed.
