# Each class had its own way

Choose the shape from what the exam rewards, then confirm it with the student on a sample. All of these live in github.com/Y3FAI/y3f under `2026-fall/<course>/`, and each folder's README is the full spec.

| Course | What the exam rewards | Shape | Reference |
|---|---|---|---|
| IT241 Operating Systems | slide recall: multiple choice that copies slide bullets, plus 2 short written questions | **card + many questions** | `it241/revision/midterm-guide-v2/` |
| SCI201 Physics 2 | understanding plus the formula sheet | **explanation-first concept cards** | `sci201/revision/midterm-guide/` |
| STAT101 Statistics | formulas plus concepts, true/false on the exam | SCI201's shape, with calculation and concept cards | `stat101/revision/midterm-guide/` |
| MATH251 Linear Algebra | short calculations from rules | **the student's own sheet as the backbone** | `math251/revision/midterm-guide/` |
| MATH251, one week (finals) | depth on one chapter | teacher-style breakdown with worked examples | `math251/final-prep/week-05/` |
| ENG103 Technical Writing | written answers | answer technique and rubrics | `eng103/how_to_make_eng103_study_guide.md` |

## IT241: card + questions

- **Built from:** the concept map and priority map (SS = asked as a written question, S = asked as multiple choice).
- **Each micro-section:** one organizing card, then many questions in the exam's patterns.
- **Never AI true/false:** the exam has none.
- **Extras:** the SS-only switch, Gantt charts for every scheduling algorithm, and three comparison sections (scheduling algorithms, sync tools, classic problems).
- **Companion page:** the top 50 predicted written questions, plus a Flooki exam of them.
- **Format:** see `it241-v2-format.md`.

## SCI201: explanation-first concept cards

**Priority map:**
- SS = on the formula sheet, S = asked on a past paper, A = bank only, B = slides only, PK = prior knowledge.
- Each concept has "builds on" links to its prerequisites.

**Cards:** one per concept, in week order, with near-duplicates merged (about 57 cards). Every part is optional:
1. **Sheet box:** the sheet's cells as printed, corrections in a silent note, then the formulas to memorize. `sheet_only` marks a card where the sheet prints only a constant (Coulomb's law: only k). Such a card is not SS.
2. **Symbols.**
3. **The explanation,** in simple language. This is the main part.
4. **A worked example.**
5. **True-or-false facts:** (statement, true?, why), read as statement → verdict → why.
6. **Past questions,** then practice from the bank.

**No "spot it" or trap parts:** the student said practice covers those.

**Source chips** on every question: Midterm PDF, Typed PDF, Bank · Ch N #i, or AI-written.

**"All together" closing part:**
- the formula sheet explained cell by cell;
- formulas asked but not printed on the sheet;
- pairs not to mix up;
- units.

**Figures:** inline SVG, replacing the bank's mermaid code.

**Companion pages:**
- a dark formula-sheet page, with a switch for explanations and units;
- a core page: SS and S cards with only the sheet box, symbols and facts;
- three Flooki exams: questions solvable with the formula sheet, traps, and concepts only.

## STAT101: SCI201's shape, two card types

- **Calculation card:**
  - a rule box: sheet formulas, then the ones to memorize, each named, with its symbols explained silently;
  - plain words;
  - "how to spot it";
  - a worked example;
  - a trap.
- **Concept card:**
  - plain words;
  - a tell-them-apart table;
  - true-or-false facts.
- **Left out:** the Critical Thinking sections, which are not on the exam.
- **Formula-sheet check:**
  - compare every "on your sheet" claim with the sheet image; a card must not claim more than the sheet prints;
  - check constants, table values and rounding conventions against the slides and the paper keys.
- **Companion pages:**
  - the SS-only switch;
  - a formula-sheet page in the printed look (Times, no LaTeX, so it looks like the exam paper);
  - a cheat sheet: SS and S concepts in one table, SS in red, with past examples and a symbols review;
  - a true-or-false sheet;
  - easy Flooki recall exams per module, meant to reinforce memory, not to trick.

## MATH251: the student's sheet as the backbone

- **The student brought a formula sheet.** Show it word for word, cut into topics in the sheet's own order, not into modules. Never remove anything from it; only add.
- **Each topic:**
  1. the sheet's rule;
  2. a clear plain-words explanation, step by step;
  3. one worked example;
  4. short bank practice;
  5. the past-midterm questions that test it.
- **Short questions only:** one formula or one small determinant. Long assignment-style calculations are left out, because the exam is short on time.
- **Closing tables, "All the rules together":** related rules from every topic side by side (solution cases, the det ≠ 0 equivalences, determinant rules), then the original sheet and the official exam sheet explained.
- **Audio:** spoken math needs care. Kokoro reads a lone "A" or "a" as the article, so spell out matrix and variable names.

## MATH251 final prep, one week in depth

- **The student's brief, in their words roughly:** they don't want to read the slides. Break the slides down so they're easy to understand, the way a teacher teaches a student, in a logical, smooth flow.
- **Shape:**
  1. a prerequisites section, with video links;
  2. then the lessons;
  3. worked examples solved step by step;
  4. every real exam question on the week, placed after the section it tests.
- See `math251/final-prep/week-05/README.md`.

## ENG103: answer technique

- **A writing course,** so the guide teaches how to write each kind of answer: define, compare, classify and justify, apply a principle, correct and explain.
- **Each kind gets** an honest rubric and objective practice.
- **Ends with** a rapid-review summary page.
- **The full method** (18 steps) is in `eng103/how_to_make_eng103_study_guide.md`.
