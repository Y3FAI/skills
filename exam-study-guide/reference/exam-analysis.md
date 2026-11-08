# Exam analysis, maps and predictions

This covers Stages 2–4 in detail, plus the predicted-questions method. The examples are from IT241 (Operating Systems, Modules 1–5).

## 1. Papers

Make one row per paper:

| Paper | Real or retyped | Format | Scope |
|---|---|---|---|
| 2021 midterm | real (scan) | 10 true/false, 10 multiple choice, 5 written | Modules 1–6 |
| 2025 midterm | retyped Word copy, no key | 30 multiple choice + 2 written | Modules 1–5 |

- **Find the pattern:** for IT241, about 20–30 multiple-choice questions and 2 short written ones. True/false appeared only in 2021, so the guide has no AI-written true/false.
- **Find the closest model paper:** the one whose scope matches the coming exam.

## 2. Weight per unit

| Unit | Questions | Slides | Questions per 10 slides |
|---|---|---|---|

The last column shows where marks per hour of study are highest. In IT241, Module 4 was the shortest deck but carried about a third of the marks.

## 3. How multiple-choice questions are made

- **Check about 15 stems against the slides.** In IT241, recent stems copy a slide bullet almost word for word and blank out the key term.
- **Wrong options are sibling terms:** controller vs driver, binary vs counting semaphore, ready vs waiting state.
- **List the repeats across years.** These go straight to S or SS.

## 4. Written questions (the hard part)

Trace every written question from every paper, including finals and units outside the scope, to the slide it is answered from. Tag each one:

- **Form:**
  - list all;
  - list some ("any two", "at least two");
  - define plus list;
  - compare a pair;
  - compare on one measure;
  - explain plus yes/no;
  - calculation;
  - "what is the main problem with…".
- **Slide type:**
  - a named or counted list;
  - a pair of terms;
  - a worked example (asked again with new numbers);
  - one mechanism with a hook;
  - code or vendor examples (never asked in IT241).
- **Learning outcome:** which weekly outcome it serves, and whether it reuses the outcome's verb ("Evaluate" became a calculation).

What IT241 showed:
- **One slide per question,** and the expected answer is that slide's bullets.
- **Teachers ask for fewer items than the slide lists,** which makes marking quick.
- **Slides under a CONTENTS heading** are about twice as likely to be asked.
- **The last unit in scope always gets a written question.**
- **Calculations repeat** on consecutive papers. **Concept questions rotate** to a neighbouring slide.
- **Slides that end with a question are bait:** one of them was asked word for word.

## 5. Concept map (Stage 3)

**Tools** (IT241's are in `~/sync/uni/2026-fall/it241/extra/revision-maps/tools/`):
- `extract_slides.py`: slide text, with images described by reading them.
- `build_concept_map.py`: the tree and the checker.

**Shape:**
- Unit → topic → concept → sub-concept, numbered.
- Each line is the slide's exact words with `[sN]`.
- Figures, tables and code are written out in full, labels as printed.
- Each unit's header holds its learning outcomes and contents slides, word for word.
- Cover, reading and thank-you slides are left out.

**The checker:**
- every quote matches its slide;
- every content slide is used.

Test it by planting a reworded quote, a dropped bullet and a missing figure.

**At the end of the map:**
- **a slide index;**
- **slide oddities,** such as an example whose answer ignores its own arrival times, or a slide from another unit copied in.

## 6. Priority map (Stage 4)

**Tags:** use the student's rules for the course (see the table in SKILL.md). Every node shows its evidence: the papers and question numbers, or the reason for an A tag.

**A tags** go to nodes that:
- are needed to answer an SS or S question;
- were asked in the test bank;
- are the same kind of calculation as an SS question (all scheduling worked examples, once SJF was SS).

**Files:**
- `priority-map.json` and `.md`;
- `past-exams.json`: every past question with paper, number, type, options, key and node;
- `bank-map.json`: bank questions mapped to nodes.

**Summary:** report a table of tag counts per unit, and list every SS item with its evidence.

## 7. Predicting the written questions

Done when the student asked for "the top 50 most likely open questions". It became `revision/predicted-50/` and a Flooki exam.

1. **Fit the patterns above** from the written questions only. The student doesn't care about multiple choice here.
2. **Profile the teacher:**
   - what kind of slide they pick;
   - how many items they ask for;
   - their phrasing ("List out… discuss each" vs "Giving the following processes…");
   - whether there are two writers.
3. **Score every slide** on those features, plus the learning outcomes that were never asked.
4. **Back-test.** Fit only on papers before the newest one, rank blind, and see where the newest paper's questions land. Report the hits and the misses honestly, and fold what the misses teach into the method.
5. **Rank and band** the predictions: #1–10 very likely, #11–25 likely, #26–40 possible, #41–50 outside chance.
6. **Write each answer** short and full-mark. Add the slide lines it rests on and why it was predicted.
7. **Order the page** by unit and slide, not by rank. Each question shows its rank as a chip.
