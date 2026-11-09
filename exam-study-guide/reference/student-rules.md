# What the student wants

These rules come from the student's feedback while the October 2026 midterm guides were built: IT241, SCI201, STAT101 and MATH251. Each rule fixed a draft the student rejected.

Most of them describe how the student studies, and hold everywhere. Some depend on the course's exam (true/false, question forms, short math questions). Fit those to the exam at hand. When the content calls for something these rules don't cover, adapt it and say why.

## The goal

- **Understanding plus exam practice.** Each section should leave the student able to answer that topic's exam questions.
- **Find out what the obstacle is for this course.**
  - **IT241:** after studying Module 1, the student found that understanding was easy. The problem was "information organization and the amount of information". The guide was rebuilt around organizing the slides, followed by many questions.
  - **SCI201 and MATH251:** the explanation was the main part ("if I understand the concept I can deal with any exam question").
  - Ask which applies to the course, or show a sample and watch the reaction.

## Organization

1. **Break the slides into the form their content needs:**
   - comparisons → a table;
   - sequences → numbered steps;
   - definitions → a term list;
   - figures → redrawn;
   - code → shown as code, with notes.

   Slides are often written badly. Dense paragraphs hide facts: the device-status table sat in a paragraph, and the student missed it until a question asked about it. Pull every fact out where it can be seen.
2. **Keep every slide line, in the slide's own wording.** Exams lift that wording. A coverage check proves nothing was dropped.
3. **Adapt each section; don't apply a template.**
   - When the student gives an example structure (say "what it is / why it exists / what it is not"), it is an example, not a template for every concept.
   - Some concepts need "what it is", some need "why it exists", some need background, some need nothing. Repeating the same headings everywhere was rejected as rigid.
   - Some structure is still wanted: adaptive structure, not none.
4. **Small, logical micro-sections, grouped into parts, in learning order.** Put comparison sections after the sections they compare.
5. **Minimal tags and labels.** The page is about content and practice.
6. **Never write "section 1.12" in any card, question or answer.** The exam never refers to the guide's numbering. "How do sections 1.12 to 1.16 fit together?" was rejected.

## Writing

- **Plain, simple words.** Not philosophical, not written in an odd way.
- **No walls of text.** Use lists and tables, and short lines.
- **Mark exam focus in red;** the student asked for red highlights. Put a red trap box on common mix-ups ("waiting ≠ ready", "full starts at 0, empty starts at n").
- **Don't add explanation that just repeats the slide.**

## Questions

- **Write realistic questions in the exam's own patterns:**
  - define;
  - list (often "any two" or "at least two");
  - explain briefly;
  - compare or differentiate;
  - calculate (for example, average waiting time from a process table).
- **No long-answer questions** such as "Describe the steps of an I/O operation, from the program's request to the result". A teacher marking hundreds of papers never asks those.
- **No questions about "the slide" or "the figure".** Exams don't ask them.
- **Match the exam's formats.** If the exam is multiple choice plus written only, write no true/false questions. Turn each past true/false question into a multiple-choice question on the same point.
- **Many questions per section,** each looking at a different part of the card. Imitate the teachers' patterns, and include some sneaky or tricky ones.
- **Choice questions first, then written ones.** Shuffle the options, so the answer isn't always A; keep "all of the above" last.
- **Math courses: only short questions.** The exam is short on time, so skip long assignment-style calculations; one formula or one small determinant is the right size.

## Answers and explanations

- **Clear, coherent and complete, with no gaps** (IT241 final, 2026-11-09). Every explanation, card and model answer must read clearly, follow logically, and leave nothing out that a student needs to answer the section's questions. Enforce it with the two-layer check in [clarity-check.md](clarity-check.md).
- **Written questions:** a box to write the answer in, then "Show the answer" to compare.
- **Model answers:** "as short as possible but fully answer full mark the question", so the student can memorize them without losing marks. Organize them as lists or short lines, never a paragraph.
- **Choice explanations are quick:** the slide line that settles the answer, then at most a short plain-words `why` of 30 words or fewer. With no slide line to quote, a short plain `why` alone.
- **Answers must be correct:**
  - re-key questions whose options don't match;
  - flag misprints on the papers and slides;
  - work disputed examples both ways (the SJF slide ignored its own arrival times).
- **When asked to add, only add.** "Add only, no removal, and fix answers." Never remove anything from the student's own formula sheet; only add to it.

## Read-along

- **The voice reads class content only.** Never provenance ("this came from the 2024 exam"), never tags. Tags are for the eyes.
- **Read exactly what is on screen, in screen order.** True/false: the statement, then "True." or "False.", then why.
- **Math must be clear when heard.** This is what made the audio useful. Give every formula a spoken form.
- **Re-voice only what changed.** The student objected to waiting for full re-renders.
- **Audio goes to R2,** never into the repo.

## Working style

- **Go step by step, and stop at each gate:**
  1. analysis;
  2. concept map;
  3. priorities;
  4. sample.

  Then build unit 1 and publish it so the student can study today. Then do the rest.
- **Don't follow instructions literally.** "Take your time and understand how we can achieve the goal, do not follow my instructions literally, see what we are trying to achieve and do better while keeping it organized and not too long."
- **When the student's earlier instructions conflict, the latest vision wins.** When they ask "let's review what we will do", restate the plan in a few bullets before building.
- **Keep the old version** until the student says to remove it ("make it v2, keep current as it is").
- **Study pages are HTML on y3f,** never chat artifacts. Always give them dark mode.
- **"push" means** commit the guide's files and push y3f.

## What was tried on IT241, and why it changed

| Version | Section shape | Student's verdict |
|---|---|---|
| Sandwich v1 | lead-in (what it is / why) → slide card → plain-words outro → questions | rigid lead-ins; then "having only questions feels dry"; the outro repeated the slides |
| v1 revised | adaptive lead-in → card → outro that breaks the slide down, red highlights | better, but cards still read like a "wall of info picked from a book" |
| **v2 (kept)** | **one organizing card → many exam-pattern questions** | "the issue is information organization… best way so far is questions" |
