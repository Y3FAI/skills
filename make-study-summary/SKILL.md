---
name: make-study-summary
description: Make an exam study summary for one unit of a university course (a module, chapter or week), step by step and never all at once. Understand the unit's content, analyse the exam patterns (including how a new exam could differ), find the core concepts, then the other exam-worthy ones; choose the summary shape this class needs (exam-question style for information-heavy classes, worked examples for math, rules and equations for physics, and so on); have Gemini organize and write it; fix it with Gemini in fix-only rounds; add highlighter markers, memory pictures (SVG) and read-along audio. Use when asked for a study summary, exam sheet, revision summary or "summary for the exam" of a unit.
---

# Make a study summary

The result is one web page per unit that a student can revise from just before the exam. It is organized the way that class is examined, written plainly, highlighted, with pictures where a picture helps memory, and narrated.

The reference build is IT241 (Operating Systems) Module 11, File Systems. The student judged several drafts. What they rejected, and why, is in [reference/lessons.md](reference/lessons.md). Read it before you start.

## The one rule: one step at a time

Each step gets your full attention.

- Do the steps in order.
- Finish a step and save its output file.
- Check the output against the step's **Done when**.
- Tell the student in a few lines what you found, then start the next step.
- **Never draft the summary before steps 1 to 5 are done.**
- Never merge steps, or skip one because it looks obvious. Most of the quality comes from steps 2 to 5, which a rushed run skips.
- Steps marked **Gate** end with the student's answer. Wait for it.

Keep the work in a folder outside the public site repo, for example `<course>/final-prep/summaries/<unit>/` in the course's own files. Copy [templates/STATE.md](templates/STATE.md) into it and tick each step as it is done. A later session continues from `STATE.md`, not from memory.

```
<work folder>/
  STATE.md            steps done, decisions, open questions
  01-content.md       step 1
  02-exam.md          step 2
  03-core.md          step 3
  04-exam-worthy.md   step 4
  05-shape.md         step 5 (the shape the student approved)
  brief.txt  r1.md    step 6 (what was sent to Gemini, what came back)
  master.md           the summary text: the single source from step 6 on
  build.py  figs.py   steps 8 and 9 (a small page builder; see examples/)
```

## Step 1 · Understand the unit's content

**Goal:** know everything the unit teaches before deciding anything about it.

- Read every slide, page or lecture of the unit.
  - Text slides: extract the text (`pdftotext -layout`).
  - Image slides: render each one and look at it. Diagrams, tables and worked examples are often images.
- Write `01-content.md`: the unit's topics in teaching order, each with its concepts in the source's own wording. Keep the source's examples and numbers, because exam calculations reuse them.
- Note what kind of content it is. Mostly definitions and facts? Procedures and formulas? Worked problems? Writing models?
- Note anything that is broken or unclear in the source: typos, contradictory numbers, missing steps.

**Done when** every slide has been read and its content placed under a topic. Spot-check 5 random slides against the file.

## Step 2 · Analyse the exam patterns · Gate

**Goal:** know how this university examines this class, not just which topics appear.

- Gather every real past paper you can. Note how trustworthy each one is: a real exam, a retyped set, or a test bank.
- For the whole course, and for this unit:
  - the question formats and their share: multiple choice, true/false, written, calculation, diagram, essay;
  - how each format is written. Multiple choice: term to definition, rule, calculation, "which is NOT". Written: define, list, compare, calculate, explain;
  - which concepts repeat across papers (concepts repeat; exact questions rarely do);
  - what the question wording lifts from the slides.
- **Consider how a new exam could differ.**
  - Weigh recent papers more.
  - Look for format changes, a new instructor, or topics new this term.
  - Plan for core concepts no paper has asked yet.
  - Never assume the next paper copies the last.
- Write `02-exam.md`: the counts, the patterns with real examples, what repeats, and what could be new.

**Gate:** show the student the patterns in a short list and ask if it matches their experience of the class. They may know things the papers don't show, like the format of this term's exam or what the instructor stressed. For example: "50 is true in my class."

## Step 3 · Find the core concepts

**Goal:** the spine of the unit: what a student must know to answer most of its questions.

- From `01-content.md`, pick the concepts the unit is built on:
  - the definitions everything else uses;
  - the mechanisms and rules;
  - the comparisons the slides draw;
  - the standard calculations.
- Mark each one asked on a past exam (★), with its paper.
- Group them by topic, in teaching order.
- Write `03-core.md`.

**Done when** each topic of step 1 has its core concepts listed, and every past-exam question on this unit maps to one of them.

## Step 4 · Find the other exam-worthy concepts

**Goal:** catch what a new exam could ask that past papers never did.

- Go through `01-content.md` again for concepts left out of step 3 that an examiner could still ask. Look for:
  - stated learning objectives;
  - anything the slides emphasize;
  - lists and comparisons (examiners love "list" and "compare");
  - numbers and named examples;
  - operations and steps;
  - traps where two terms are easy to confuse.
- **Run a coverage check.** List the content words and phrases in the source that appear nowhere in your concept lists. Everything left over should be boilerplate (slide numbers, book titles). In Module 11 this caught two missing operation lists.
- Write `04-exam-worthy.md`. For each concept, say why it is exam-worthy.

**Done when** the coverage check leaves only boilerplate.

## Step 5 · Choose the summary shape for this class · Gate

**Goal:** the shape that serves this class and its exam. This is the most important decision.

Pick it from what steps 1 to 4 found: the kind of content and the exam's formats. [reference/shapes.md](reference/shapes.md) has the shapes that fit different classes, for example:
- information-heavy classes get **exam-question style**: key terms, rules as question and answer, written questions with model answers, calculations, traps;
- math gets **worked examples** and method steps;
- physics gets **rules and equations**, each with when it applies and one standard problem;
- statistics gets a **decision guide**: which method, when, and how to interpret the result;
- writing classes get **models and templates**.

Mix shapes when the unit mixes content: a calculation topic inside a fact-heavy unit gets worked examples.

- Write `05-shape.md`:
  - the shape;
  - the block order inside each topic;
  - which question formats to use. Only the exam's own: if the exam has no true/false, the summary has none, not even yes/no questions;
  - what to highlight;
  - which pictures to plan.
- Build a **sample of one topic** in that shape. It can be rough, but it must be real content.

**Gate:** show the student the shape and the sample, and wait for their verdict. Rework the shape until they approve it, and record the decision in `05-shape.md`.

## Step 6 · Gemini organizes and writes

**Goal:** a well-organized, plainly written summary. Gemini writes the words; you own the facts.

- Use the `user-writer-in-browser` skill (Gemini in the student's logged-in browser), and send only course facts. [reference/gemini.md](reference/gemini.md) has the brief for summaries:
  - who reads it and for which exam;
  - the approved shape and the topic order;
  - the student's rules;
  - the checked facts from steps 3 and 4, with the exact numbers;
  - the output inside one code block.
- Save the answer as `r1.md`, then turn it into `master.md` in the agreed markdown format. From now on `master.md` is the text.

**Done when** `master.md` has every topic and every block of the shape.

## Step 7 · Fix the issues with Gemini

**Goal:** a summary with nothing wrong, nothing missing, and nothing the exam doesn't use.

- **Review `master.md` slowly**, using the checklist in [reference/gemini.md](reference/gemini.md):
  - facts against steps 3 and 4, and every number recomputed;
  - dropped concepts and dropped written questions (rewrites drop them);
  - question formats the exam doesn't use;
  - definitions placed before their terms;
  - duplicates.
- **Have a fresh reader test it.** Give a new agent only the page and a quiz built from past questions and the bank, without the answer key. It answers closed-book, then lists what was unclear or missing. Each gap becomes a fix.
- **Send fix-only rounds:** numbered issues, and ask for REPLACE/WITH and ADD TO lines inside a code block, never the full text again. Stitch the changes into `master.md` yourself. Each REPLACE must match exactly once; if one doesn't, ask Gemini for that line again instead of guessing.
- If you change wording yourself (a duplicate removed, a word added), tell the student.

**Done when** the review checklist passes, every number checks, and the fresh reader's gaps are fixed.

## Step 8 · Improve it: markers, pictures, layout

**Goal:** a page that is easy and pleasant to study from. [reference/page.md](reference/page.md) has the details that worked.

- **Markers:** soft highlighter colours behind the words, one meaning per colour (term, answer to say, result, trap), and one key phrase per answer. Never a stroke under the text.
- **Pictures:** an SVG wherever a picture connects things better than words:
  - structures and hierarchies;
  - a process or chain;
  - a layout on disk or in memory;
  - a calculation's geometry;
  - two things side by side.

  Pictures only add: they remove nothing. Every number in a picture comes from the summary's own examples, so the picture and the text reinforce each other.
- **Layout:** dark background, a wide reading column, generous vertical spacing. No sticky header, and no gimmicks the student didn't ask for.
- Build the page with a small script from `master.md` (see [examples/it241-module-11/](examples/it241-module-11/)). Screenshot every section and every picture, and fix what looks wrong before showing it.

**Done when** the screenshots look right, every SVG parses, and nothing was removed from `master.md`.

## Step 9 · Add read-along · Gate

**Goal:** audio the student can listen to while reading. It reads what is on screen, in screen order.

- Use the `read-along` skill. [reference/read-along.md](reference/read-along.md) covers what is specific to summaries:
  - a spoken form for symbols, abbreviations, bit strings and pairs;
  - a longer pause after each question, so the listener can answer first;
  - pictures stay silent;
  - the shared player's styles must not override the page.
- Read the spoken script before voicing. After rendering, separate the false alarms (homophones such as "disc" for "disk") from real misreadings, and fix only the real ones.

**Gate:** open the page for the student, with the player working.

## Step 10 · Publish and learn

- Link the page from the course page, refresh any mirror, and update the course's status file.
- Commit only the summary's own files. Push when the student says so, or when they have told you to push finished summaries without asking.
- Keep `master.md` and the builder with the work folder, not in a scratch folder that can be wiped.
- Add any lasting lesson from the student's feedback to [reference/lessons.md](reference/lessons.md), so the next unit starts from it.

## Next units

Once the student approves the first summary, the other units reuse its shape and builder. They still go through steps 1 to 7 one at a time, because each unit's content and exam weight differ. Steps 8 and 9 then mostly reuse what exists.
