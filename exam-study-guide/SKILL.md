---
name: exam-study-guide
description: Build a university exam study guide (a midterm or final revision web page) from a course's slides, past papers and question banks. Follow a flexible path, adapted to each course: understand how the exam is written, map the material, set priorities from evidence, organize it into small sections, show a sample, then build cards and exam-style questions with read-along audio. Use when asked to make a study guide or revision guide, a concept or priority map, or predicted exam questions, or to work out how a course's exams are written.
---

# Exam study guide

This skill helps you turn a course's materials into one web page the student studies from before an exam. It distils how the y3f midterm guides were made in October 2026. The guide the student called great is IT241's (`2026-fall/it241/revision/midterm-guide-v2/` in github.com/Y3FAI/y3f).

## Adapt it first

Courses differ a lot. Before you start, look at four things:

- **The subject:** recall-heavy, formula-heavy, calculation, or writing.
- **The resources:** clean slides or image-only decks, many past papers or none, a test bank, a formula sheet, the student's own notes.
- **The units:** a few big chapters or many small weeks.
- **The exam:** its format, and how much time is left before it.

Then shape the guide to fit. Everything below is a **default path and a set of examples**, not a template:

- **Steps:** skip, merge or reorder them. A course with no past papers can't have an evidence-based priority map. A student with one evening needs a short core page, not a 100-section guide.
- **Section shape:** the IT241 shape (card + questions), the SCI201 shape (explanation first) and the MATH251 shape (the student's own sheet) each fit their course. A new course may need a mix, or something new. Content inside one guide can differ too: a calculation topic and a definitions topic don't need the same parts.
- **Checks:** the build checks listed here are ones that caught real mistakes. Keep the ones that fit; write new ones for the new material.

**When you change the default, say so briefly and why.** Agree the shape with the student on a sample before building it all. What never changes is the student's way of studying, in [reference/student-rules.md](reference/student-rules.md). Even those rules adapt to the course's exam: "no true/false" applies only when the exam has none.

## Useful context

- **Where things go:** the workspace's `AGENTS.md`. In the y3f setup:
  - sources are in `~/sync/uni/<term>/<course>/` (`slides/`, `extra/banks/`, `extra/revision-maps/`);
  - pages are in `~/dev/y3f/<term>/<course>/revision/<name>/` or `final-prep/<unit>/`, linked from the course's `content.json`, then mirrored.
- **Shapes that worked, and why:** [reference/course-variants.md](reference/course-variants.md).
- **Other skills:** `read-along` for audio, `flooki-exam` for online practice exams.

## The default path

### 1 · Gather and scope

- List what exists: slide decks (text and images), past papers, test banks, the formula sheet, the course plan, earlier guides and banks.
- Note how trustworthy each past paper is: a real exam, or a retyped set of unknown origin.
- Confirm the scope, the format and the date. Ask only for what you can't find.

### 2 · Understand the exam · show the student

Go beyond counting topics; the student called that shallow. Work out:

- how questions are written;
- which units carry the marks for their size;
- what repeats across years;
- for written questions, which kind of slide they come from and which form they take (list, compare, calculate…).

Use whatever the papers allow. With few or no papers, use the test bank, the learning outcomes and the course plan, and say how thin the evidence is. Methods that worked: [reference/exam-analysis.md](reference/exam-analysis.md).

### 3 · Map the material · show the student

- Build a map of every concept in scope, in the slides' own wording, organized in a hierarchy.
- Check it against the slides, so nothing is lost.
- How detailed it is depends on the course. IT241 needed every bullet, because its exams lift slide wording. A formula course may be better mapped by formula and concept.

### 4 · Set priorities · show the student

- Tag concepts by the evidence: past exams, the formula sheet, the bank.
- Keep everything in the map. A priority sets study time, not whether a concept is in.
- The scale and what each tag means are the student's call, per course. See the examples in `exam-analysis.md` §6.

### 5 · Plan and sample · get approval

- Plan small sections in learning order, grouped into parts. Add comparison sections where students mix things up.
- Pick each section's parts to suit its content.
- Build one or two sample sections (with audio, if the page has read-along) and wait for the student's reaction before building the rest.

### 6 · Build, one unit at a time

- Publish the first unit early, so the student can start studying, then continue.
- Put real past questions on the section they test, add bank questions, and write new ones in the exam's patterns.
- Let a build script catch mistakes. These caught real ones before:
  - a concept left out;
  - a past question placed twice;
  - a quote that isn't on its slide;
  - an explanation that's too long;
  - a question type the exam doesn't use;
  - text that points at a section number;
  - a symbol the voice can't read.

  Adapt the list to the material.
- **Check that every explanation is clear, coherent and complete, with no gaps.** The student asked for this for the IT241 final (2026-11-09). Do it in two layers:
  - **Build checks** catch the gaps a script can see:
    - an answer that no card up to that section teaches;
    - an explanation that never states its answer;
    - a written answer with fewer points than the question asks, or a comparison with one side;
    - a question a slide asks that the card leaves open;
    - an abbreviation used before it is spelled out.
  - **A clarity review** covers what only a reader can judge.
    - Someone who didn't write the section reads it as a student: a fresh agent or the student.
    - They answer every question from the cards alone, then judge each section clear, coherent, complete and answerable.
    - The build refuses to publish a section without a passing review for its current content, keyed by a hash of the section, so any edit asks for a new review.
  - The IT241 final guide is the reference: [reference/clarity-check.md](reference/clarity-check.md).
- Give the page dark mode.

### 7 · Read-along

- The voice reads the study content, in screen order. Questions, tags and sources stay silent.
- Math and symbols need spoken forms.
- Use the `read-along` skill. Audio goes to R2, never into the repo.

### 8 · Review and iterate

- Read the cards as the student would, and fix what's unclear before they find it.
- Apply the student's feedback across the whole guide, and note any lasting rule in the guide's README or in `student-rules.md`.
- For a big change of direction, build a new version beside the old one, and keep the old one until the student says to remove it.

### 9 · Extras, if asked

For example: a switch to show only the top-priority sections, predicted questions, a cheat sheet, a formula-sheet page, a true-or-false sheet, or Flooki exams. See [reference/companion-pages.md](reference/companion-pages.md).

## Publish

- Link the page from the course's `content.json`, mirror it, and update the workspace's status page.
- Commit only the guide's files, and push when the student says "push".
- The site is public: no names, IDs, grades or exam-paper scans.
