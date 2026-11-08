---
name: flooki-exam
description: Make practice exams on Flooki (flooki.app) from course material such as past exam papers, a question bank, slides or a formula sheet, then publish them through the Flooki agent API and return the shareable exam link. Use when asked to make a Flooki exam, a mock or practice exam, or to turn past papers or a question bank into an online quiz.
---

# Flooki exam: course material → checked questions → a link on flooki.app

Flooki is an exam app with a dark exam screen. An exam has a title, optional metadata and 1–500 questions of three types: multiple choice, true/false and short answer (graded out of 3). Questions render Markdown, KaTeX math (`$…$`, `$$…$$`), code blocks, and figures as inline SVG or Mermaid. The API creates an exam and answers with its URL; there is no edit endpoint.

Any agent can use this skill. The tool is one Python 3 file with no dependencies. An agent without a shell can follow the same file format and send the request itself (`reference/api.md` has curl and fetch examples).

## Folder map

```
flooki-exam/
  SKILL.md                    this file
  tools/flooki.py             check | show | shuffle | payload | publish
  reference/api.md            the Flooki agent API: body, question schema, errors
  reference/flooki-prompt.md  Flooki's own rules for writing questions (from its how-to page)
  examples/minimal.json       one question of each type; copy it to start
```

## Workflow

1. **Find the sources and read them yourself:** past papers (often photos or PDFs), the question bank, slides and formula sheet. Typed question sets often have wrong keys, and photos hide question numbers. Note what is missing.
2. **Decide what the exam is.** Ask only if the request leaves it open:
   - **Past paper as is:** one exam per paper, in its order.
   - **Filtered set:** past questions that meet a rule, such as "solvable with the formula sheet", with a cap and a top-up from the bank (see below).
   - **Mock exam:** new questions in the style, topics and difficulty of the past papers, with new numbers. This is Flooki's rule 4: the past papers are the only source when there are no slides.
3. **Key every question yourself.** Compute each numeric answer in code, not in your head, and check a given key before trusting it. When a source question is broken (a wrong unit in the key, numbers that contradict the wording, two identical options, a distractor that is also correct), fix it as little as possible. Tell the user what you changed in your reply, never inside the question.
4. **Write the exam file** (format below). Keep it next to the course's other exam data, with a small script that builds it when it comes from structured sources, so it can be rebuilt.
5. **Check it, shuffle it, read it:**
   ```sh
   F=path/to/flooki-exam/tools/flooki.py
   python3 $F check EXAM.json      # every API rule, plus warnings: duplicates, open $, source talk, answer pattern
   python3 $F shuffle EXAM.json    # seeded shuffle of multiple-choice options; "All of the above" stays last
   python3 $F show EXAM.json       # read it the way a student will, with the key marked
   ```
6. **Publish and record the link:**
   ```sh
   python3 $F publish EXAM.json --dry-run
   python3 $F publish EXAM.json    # prints the URL and writes it into the file under "published"
   ```
   Add the link wherever the course lists its exams. Then give the user the URL, the question count, what was kept or left out and why, and anything you corrected.

## The exam file

It is the API body, except that `questions` is a plain array (the tool turns it into the JSON string the API wants):

```json
{
  "title": "SCI201 Midterm Practice: Formula Sheet Questions",
  "description": "≤ 500 characters, shown under the title",
  "metadata": {"subject": "SCI201", "institution": "Saudi Electronic University", "examType": "midterm"},
  "questions": [
    {"type": "multiple_choice", "topic": "Magnetic force", "text": "…", "options": ["…", "…", "…", "…"],
     "correctIndex": 2, "explanation": "…", "source": "2024 Q6"}
  ]
}
```

- `examType` is `quiz`, `midterm`, `final` or `other`. `other` needs `customExamType` (≤ 50 characters), and the others must not have it.
- Fields Flooki doesn't know, such as `source`, stay in the file for your records and are stripped before sending. Use `source` to note where each question came from ("2023 Q10", "bank 24:20").
- Never send `points` or `isPublished`.

## Choosing questions: filters, caps and top-ups

Use this when the user says, for example, "only questions on the formula sheet, at most 30, top up from the bank":

1. **List the sheet cells exactly as printed.** Look at the image; don't work from memory.
2. **Write down every formula each question needs.** Keep the question only if all of them are printed. Constants and unit prefixes count as given. Conceptual questions stay only when a printed formula answers them, for example "F_B is largest at 90°" or "no magnetic force on a charge at rest" from F_B = |q|vB sinθ.
3. **Watch the traps.** A law is not on the sheet just because its constant is: Coulomb's law is not, even when k is printed. Misprints count too: one sheet printed k as 8.9×10⁻¹⁹ C, so use the correct value, 8.99×10⁹ N·m²/C², in explanations.
4. **Remove repeats.** Past papers reuse questions with new numbers. Keep one per calculation, unless the second one adds a real twist (a negative charge, a charge of 2e, a different unknown).
5. **Cap the count, then top up from the bank** with questions for the sheet cells no kept question uses, so the exam covers the whole sheet. Never top up with a near copy of a kept question.
6. **Report the result:** kept, left out (and why) and added.

## Writing rules

Flooki's own rules are in `reference/flooki-prompt.md`; follow them. In short, and with what worked in practice:

- **Each question stands alone.** No "as in the slides", "from the bank", file names or citations, in any field. `check` warns about these.
- **Explanations:** the answer first, then one to three sentences on the idea, then "Why not the others" only for close or common mistakes. Show the working for calculations as display math. For short answers, put the expected answer and its accepted forms in `correctAnswer`: "$r = 0.857\ \Omega$ (about $r = 0.86\ \Omega$)".
- **Multiple choice:** four options. Distractors should be real mistakes: a forgotten sin θ, cm left unconverted, multiplying instead of dividing. If the source has only two choices, add two distractors like that and explain them. Shuffle, so the right answer is not mostly A.
- **True/false:** options exactly `["True", "False"]` (or the source language's words).
- **Math:** `$…$` inline and `$$…$$` display, never `\(…\)`. In a JSON file every backslash is doubled (`\\frac`); in code, write it once and let the JSON encoder escape it. Units go in `\text{ }`.
- **Language:** match the source material unless told otherwise.
- **Figures:** use `img`, with inline `<svg>…</svg>` or Mermaid code. No image links, no base64.
  - The exam screen is dark, so draw with light colours: white or light-grey strokes and light-blue labels. Use `fill="none"` for open terminals.
  - Make the figure carry every value the question needs.
  - The SVG must be **well-formed XML**, because Flooki shows it through `<img src="data:…">`. A tag left open (an unclosed `<tspan>`) works inline in HTML but shows a broken image on Flooki. `check` parses every SVG.
  - Render it once on a dark background and look at it before publishing. After publishing, open the exam and look at the figure question.

## Token and publishing

- The tool reads `FLOOKI_SERVICE_TOKEN`, then the `.env` given with `--env-file`, then `~/.config/flooki/token`. If a project keeps it in a `.env`, pass that file. Otherwise the user saves it once, from the clipboard, so it never appears in a chat (in Claude Code the user runs it with a leading `!`):
  ```sh
  mkdir -p ~/.config/flooki && pbpaste > ~/.config/flooki/token && chmod 600 ~/.config/flooki/token
  ```
- **Never print, echo, log or commit the token, and don't go searching for it.** If it is missing, ask the user to save it as above.
- Publishing is outward-facing: anyone with the link can open the exam. Publish when the user asked for the exam to be made.
- `publish` skips a file whose content is already published. Flooki can't edit an exam, so `--again` makes a new exam with a new link; the old link keeps the old content. The file keeps the old links under `published_before`.
- `publish` retries network errors and 5xx answers; flooki.app sometimes resets connections. An HTTP 4xx prints Flooki's error code and what it means (the full list is in `reference/api.md`).

## Pitfalls learned the hard way

- **Bank copies drift from the paper.** A bank copy of a past question may carry different numbers (0.062 Ω where the paper printed 0.06 Ω) or different choices. If the exam is "from the papers", use the paper's own numbers and choices.
- **Keys in typed sets are often wrong:** joules for watts, an answer ten times too big, a "gold" wire with copper's resistivity. Recompute them.
- **Ambiguous distractors:** an option like "U = −qEd" next to "ΔU = −W" can also be read as right. Replace it.
- **Rendering:** checked on 2026-10-20, the exam page bundles remark/micromark (Markdown), KaTeX and Mermaid, so bold, lists and math all render. Plain-text explanations work too.
