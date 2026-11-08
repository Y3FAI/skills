---
name: exam-study-guide
description: Build a university exam study guide (a midterm or final revision web page) from a course's slides, past papers and question banks. The process is a deep exam analysis, a complete concept map in the slides' exact wording, evidence-based SS/S/A/B priorities, micro-sections in learning order, a sample for approval, then cards plus exam-pattern questions with build checks, read-along audio and companion pages. Use when asked to make a study guide or revision guide, a concept or priority map, or predicted exam questions, or to work out how a course's exams are written.
---

# Exam study guide

This skill turns a course's slides, past papers and question banks into one web page the student studies from before an exam. The page has organized cards that hold every slide line, many questions in the exam's own patterns, and read-along audio.

It is the process behind the y3f midterm guides of October 2026. The reference implementation is the IT241 guide, `2026-fall/it241/revision/midterm-guide-v2/` in github.com/Y3FAI/y3f (the student called it great).

The process runs in stages. **At each gate, stop, show what you made, and let the student steer.** The student sharpens the vision while studying, so expect changes. The latest instruction wins over earlier ones.

## Before you start

- **Read the workspace instructions** (`AGENTS.md`) for where sources live and where pages go. In the y3f setup:
  - Sources are in `~/sync/uni/<term>/<course>/`: `slides/`, `extra/banks/` and `extra/revision-maps/`.
  - Pages go in `~/dev/y3f/<term>/<course>/revision/<name>/`, or in `final-prep/<unit>/` for finals.
  - Each page is linked from the course's `content.json`, and then the mirror script is run.
- **Read [reference/student-rules.md](reference/student-rules.md).** It distils the student's feedback from building these guides. First drafts mostly fail on these rules.
- **Pick the course's shape** in [reference/course-variants.md](reference/course-variants.md). Each class needed its own: card plus questions for slide-recall courses, explanation-first cards for formula-sheet courses, a sheet-driven page when the student brings their own sheet. Confirm the choice with the student.
- **Use the other skills:** `read-along` for audio, `flooki-exam` for online practice exams.

## Stage 1 · Gather and scope

- List every source:
  - slide decks per unit (text and images: many slides are pictures);
  - past papers and test banks;
  - the formula sheet, if there is one;
  - the course plan, for what the exam covers;
  - any earlier guides or banks.
- **Label each past paper:** a real exam (a scan, photo or Blackboard export) or a retyped set of unknown origin. This decides the source chips and how far to trust the keys.
- Confirm the exam's scope (units), its format (multiple choice, true or false, written, calculation) and its date. Ask only for what you cannot find.

## Stage 2 · Analyze the exam · gate

Go to the level of question forms. The student rejected a topic count as "shallow, not analytical". The method is in [reference/exam-analysis.md](reference/exam-analysis.md).

1. **Per paper:** how many questions of each type, the marks, and the time allowed.
2. **Per unit:** the number of questions, and questions per 10 slides (the marks per hour of study).
3. **How multiple-choice stems are made:** usually a slide bullet with its key term blanked, and wrong options that are sibling terms. Note which questions repeat across years.
4. **Every written question**, each traced to the slide it is answered from:
   - its form: list all, list some, define plus list, compare a pair, compare on one measure, explain plus yes/no, calculation, or "what's the problem";
   - the kind of slide it came from: numbered list, pair of terms, worked example, or a question printed on the slide.

Report this with tables, then **stop**.

## Stage 3 · Complete concept map · gate

Build the map without priorities first.

- **Coverage:** every concept from every deck in scope, including what sits in figures, tables, code and worked examples.
- **Hierarchy:** unit → topic → concept → sub-concept, numbered like `3.3.2.4`.
- **Wording:** each entry in the slide's exact words with its slide number (`[s17]`), typos kept.
- **A checker proves completeness:**
  - every quote matches its slide word for word;
  - every content slide is used;
  - test the checker itself by planting a reworded quote and a dropped bullet, and confirm it catches both.
- **Extras:**
  - a slide index: each slide and the entries that use it;
  - a list of slide oddities: errors, duplicated slides, examples that contradict their own data.
- **Save** `concept-map.json` and `.md` and `slides.json` in the course's `extra/revision-maps/`.

## Stage 4 · Priority map · gate

Tag every node, and keep every node: a priority sets study time, not whether a concept is in.

The scale is the student's, per course, so ask. These were used:

| Tag | IT241 (slide recall) | SCI201, STAT101, MATH251 (formula sheet) |
|---|---|---|
| SS | asked as a written (open) question in a past exam | on the formula sheet |
| S | asked as a multiple-choice question in a past exam | asked in a past paper |
| A | needed for an SS or S node, in the test bank, or clearly important | in the bank only, or a core idea |
| B | everything else | on the slides only |

- **Evidence:** each tag shows it, as paper and question number.
- **Also write `past-exams.json`:** every past question transcribed, with paper, number, type, options, key and the node it tests.
- **Understanding-heavy courses (SCI201):** add "builds on" links, so each concept lists what it needs first. Add PK for prior knowledge.
- **Off-exam parts** (STAT101's Critical Thinking sections): mark them and leave them out.

## Stage 5 · Plan and sample · gate

- **Plan the page** as units → parts → small sections in learning order (`src/plan.py`):
  - each section lists the concept-map nodes it covers;
  - add comparison sections (with no nodes of their own) after the sections they compare;
  - titles name the topic.
- **Agree the design:** which earlier guide it should look like, read-along or not, and as few tags and labels as possible.
- **Build one or two sample sections,** with audio if the page will have read-along, and **wait for approval.** Never build the whole guide on a format the student hasn't seen.

## Stage 6 · Build, one unit at a time

- **Order:** finish and publish the first unit, so the student can study it the same day, then do the rest.
- **What each section holds** depends on the course's shape. The IT241 shape ([reference/it241-v2-format.md](reference/it241-v2-format.md)) has two parts:
  1. **One card** that organizes all of the section's slide lines.
  2. **Many questions:** every past-paper question exactly once, the test-bank questions, and new ones written in the exam's patterns, some of them tricky.
- **The build script enforces the rules** and stops on a failure:
  - every concept of a built unit is on a section;
  - each past question is placed exactly once;
  - no written question repeats another;
  - every quoted slide line is really on that slide;
  - every `why` is 30 words or fewer;
  - no AI-written true/false when the exam has none;
  - no text points at a section number;
  - every narrated symbol has a spoken form.
- **`--cover`** lists slide lines that no card covers. Fix each one, or note why it is left out.
- **After every build,** run `dark-mode.py`. The student asked for dark pages because bright ones hurt their eyes.

## Stage 7 · Read-along

- **The voice reads content only:** section titles and cards, or the teaching parts in other shapes.
- **Silent:** questions, tags, labels, sources, code and notes about the slides.
- **True/false facts** are read as the statement, then "True." or "False.", then the why.
- **Every symbol** has a spoken form.
- **Run the `read-along` skill:** `plan` → `status` → `voice` → `render` → `publish`.
  - Audio goes to R2 (`media.y3f.me/<course>/`), never into the repo.
  - A rebuild drops the player, so always finish with `publish`.

## Stage 8 · Review and iterate

- **Read every card as the student would,** yourself or with one sub-agent per unit:
  - Is it clear and organized?
  - Does any question ask something the card hides?

  Fix problems before the student finds them.
- **Feedback comes as short messages** ("explanations are too long", "that will never be asked"):
  - apply it to the whole guide, not just the example;
  - rebuild and republish the audio;
  - write the rule down: in the guide's README, and in `reference/student-rules.md` if it applies to every guide.
- **For a change of direction,** build the new version next to the old one (`midterm-guide-v2/`). Remove the old one only when the student says so.
- **The guide's README** records what each section holds, the file layout, the build and audio commands, and what the build checks.

## Stage 9 · Companion pages (on request)

The student may ask for:
- an SS-only switch;
- the top N predicted written questions;
- a cheat sheet;
- a formula-sheet page;
- a true-or-false sheet;
- a core page;
- Flooki exams.

See [reference/companion-pages.md](reference/companion-pages.md).

## Publish

- Link the page from the course's `content.json`, run the mirror script, and update the workspace's status page.
- Commit only the guide's own files. Push only when the student says so; they usually just say "push".
- The site is public: no names, IDs, grades or exam-paper scans.
