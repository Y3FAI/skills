# Gemini: brief, review, fix-only rounds

The mechanics (opening Gemini, `gemini.sh send` and `wait`, checking that a send really posted) are in the `user-writer-in-browser` skill. This page covers what is specific to study summaries.

**Send course facts only.** No names, IDs, grades or personal data.

## The first brief (one full request)

Write it to `brief.txt`, in plain sentences. A brief of about 26,000 characters, draft included, worked; Gemini took about 5 minutes to answer.

```
I need help organizing and writing an exam revision summary for <course>, <unit>.
Reader: a university student revising just before the final. The exam has <formats and counts>.

What the student said about earlier drafts:
- <their complaints, quoted, e.g. "the concept is above the thing", "badly organized for ease of reading">

Shape (approved): one section per topic, in this order: <topics>.
Inside each topic, these blocks in this order: <blocks from 05-shape.md>.
Rules:
- <the student's rules, e.g. term first then meaning; no true/false or yes/no questions; short model answers as bullets>
- Plain words, short lines, no filler. Add no fact that is not below.

Checked facts (the only source):
<facts from 03-core.md and 04-exam-worthy.md, with exact numbers and worked calculations>

Current draft (if any) and its problems:
<draft>
1. ...

Output: the whole summary inside ONE code block (```markdown … ```) using exactly:
## N. Topic        ### Block        - **Term**: meaning        - **Question?** Answer
**Q. Written question**  followed by "- " answer lines.
After the code block, two lines saying what you changed.
```

Ask for a code block every time. The reader returns the page's visible text, and without a code block the `#`, `**` and `-` symbols are lost.

## Review checklist (step 7)

Real mistakes Gemini made on Module 11:

- **Dropped content.** Its rewrite dropped about 25 written questions and all the contiguous-allocation problems. Compare it with your fact files topic by topic, and count the written questions before and after.
- **Question formats the exam doesn't use.** It kept 20 yes/no questions ("Is FAT a fourth method? No…"). Each must become what, which, why or how: "FAT is a variation of which allocation method?"
- **A question that doesn't match its answer.** "Where do file locks come from? They are similar to reader-writer locks."
- **Definition before term.** Write "Partition: a subdivision of a disk, also called a minidisk or slice", not "Minidisks or slices: other names for partitions".
- **Lost details:** an argument (`mkdir dir-name`), half of a fact ("NTFS keeps both … in the master file table"), units ("blocks of 512 units", not "512-byte blocks").
- **Inconsistent models:** calculations must all use the unit model the summary states.
- **Duplicates:** new traps that repeat a rule or a written question. Keep one copy.
- **Numbers:** recompute every one in code, not in your head.

## Fix-only rounds

Never ask for the full text again: it is slow, and every rewrite drops content. Send numbered issues, and ask for:

```
Send only the changes, inside one code block:
REPLACE: <exact current line>
WITH: <new line or lines>
ADD TO: <Topic> / <Block>
<new lines>
After the code block, one line: how many REPLACE and ADD TO entries you sent.
```

- Stitch the changes into `master.md` yourself (Module 11's `stitch.py` did this).
- Each REPLACE must match exactly once. Matching may ignore `- ` and `**`. If one doesn't match, ask Gemini for that line again.
- Check the count line against what you applied.
- Ask for a full topic again only when its structure changes.

## Wording you change yourself

Keep Gemini's words. When you must change something (remove a duplicate, add a slide example such as "such as Veritas", choose which phrase gets highlighted), keep it small and tell the student what you changed.
