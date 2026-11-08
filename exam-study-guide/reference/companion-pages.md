# Companion pages

Pages the student asked for once a guide existed. Build each one only when asked. Reuse the guide's CSS and voice helpers, so the pages look the same and their spoken lines match.

## SS-only switch (IT241, STAT101)

- **The control:** a switch under the map or contents, remembered per browser (`src/page.js`). It hides every section whose tag is not SS.
- **Markup:**
  - sections and map links carry `data-tag`;
  - bands and map groups carry `data-ss` (0 hides them).
- **Audio:** hidden sections also get `data-ra-off`, and the shared player (`assets/read-along.js`) skips any line inside one. The audio then reads only what is shown: on IT241, 116 of 1,057 lines (about 10 of 108 minutes).

## Top N predicted written questions (IT241 `revision/predicted-50/`)

- **The method** is in `exam-analysis.md` §7.
- **Order:** by unit and slide, not by rank.
- **Each question shows:**
  - its rank as a chip;
  - its data;
  - a writing box, kept in the browser;
  - **Show the answer**, which opens the short full-mark answer, an "In plain words" line where one helps, the slide lines it rests on, and why it was predicted.
- **Filters:** All 50, Top 25 or Top 10. Hidden questions get `data-ra-off`.
- **Also made:** a Flooki exam of the same questions, and a 100-question version in Markdown.

## Cheat sheet (STAT101 `revision/cheat-sheet/`)

- **One table** covering every SS and S concept: concept and formula beside a short explanation, in week order.
- **SS rows** are red, with the sheet's printed lines in Times. Where a past midterm asked an SS row, show that question with its answer and working.
- **Symbols review** closes the page: each symbol is one read-along line, "name: meaning". It flags clashes, such as E meaning two things on the sheet.
- **The build fails if:**
  - an SS or S concept is missing;
  - a row points at the wrong card;
  - an example belongs to another concept.

## Formula-sheet page (SCI201, STAT101)

- **The printed cells** in the sheet's own order and layout, on a dark page.
- **STAT101** sets them in the printed one-line look (Times, no LaTeX), so the student recognizes them on the exam paper.
- **A switch,** or a tap on one cell, shows:
  - what the cell means;
  - its symbols, with units;
  - how to read unclear printing;
  - links to the cards that teach it.

## True-or-false sheet (STAT101 `revision/tf-sheet/`)

- **Key ideas in plain words, no formulas:** every concept a past exam asked as true or false, plus the bank's most-asked ones.
- **Under each idea,** real statements read as statement → True/False → why.
- **Checks:** the counts are computed from `past-exams.json` and the bank, and the verdicts are checked against the keys.

## Core page (SCI201 `revision/midterm-core/`)

- **Contents:** the SS and S cards with only their sheet box, symbols and true-or-false facts. Built with the guide's helpers.
- **Audio:** copy the guide's audio cache folders in first, so almost nothing needs voicing again.

## "All the rules together" tables (MATH251)

Fragmented rules from every topic, combined into one table per theme: solution cases, the det ≠ 0 equivalences, determinant rules, transpose vs inverse. The student asked for these after studying: "there are many fragmented rules but one table that holds many rules".

## Flooki exams

Use the `flooki-exam` skill. Exams that worked:
- **From past papers only:** at most 30 questions, topped up from the bank.
- **Questions solvable with the formula sheet.**
- **Concepts only:** no calculation, true/false and multiple choice.
- **Traps:** one named mistake behind each wrong choice.
- **Recall:** easy true/false and multiple choice per module, to make the student recall rather than reread ("not challenging or tricky; its goal is to reinforce and cover all concepts and small sub-concepts").

Link each exam on the course's `content.json` and always publish it. The student said "we always push to flooki".
