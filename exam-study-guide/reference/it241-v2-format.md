# The IT241 v2 format (reference implementation)

The live guide is in `2026-fall/it241/revision/midterm-guide-v2/` (github.com/Y3FAI/y3f). Its `README.md` and the docstring at the top of `build.py` are the full spec. It's a worked example, not a template. Reuse what fits, such as the card markup, the practice-item format and the checks, and change what the new course needs. A course with formulas, diagrams or no slide text will need other parts and other checks.

## Files

```
build.py        reads src/ and the revision maps; checks everything; writes index.html
dark-mode.py    the lights-off theme; run after every build
readalong.json  config for the read-along skill
src/plan.py     units → parts → sections, each with the concept-map nodes it covers
src/m1.py …     SECTIONS = {id: dict(card=…, practice=[…], say={…})}; a unit is on the page once its file exists
src/notes.py    hand-written fixes for past and bank questions, keyed by question id
src/figures.py  redrawn figures and Gantt charts
src/page.js     the SS-only switch (remembered per browser)
src/*.css       base, guide and v2 card styles; tables of 3–5 columns stack on phones
```

## Card markup

One block per paragraph or run of lines:

```
### Heading              a heading inside the card
- item / 1. item         lists; indent two spaces to nest
Term :: meaning          a run of these is a two-column term list
| a | b |                a table; the first row is the header
> text / !> text         a note / an exam trap (red box)
~> text                  a note about the slides themselves (a typo, a source); not read aloud
```                      code
[[fig 1,13]]             the redrawn figure of unit 1, slide 13
[[gantt key]]            a Gantt chart, or runs written "P1 0-24, P2 24-27"; every bar labelled
[[flow A | B | C]]       a short chain of steps with arrows
inline: **bold**, *italic*, `code`, ==exam focus== (red)
```

## Practice items

```python
dict(past=["mid241:9"])                     # a past-paper question, by paper:number (past-exams.json); placed exactly once
dict(bank="ch6:Multiple Choice 12")         # a test-bank question, by chapter:label
dict(past=["mid2021:5"], q=..., options=[answer, ...], quote=(slide, "words"))
                                            # a past true/false asked as multiple choice; the label adds "from true/false"
dict(q="...", options=["right answer", "wrong", ...],
     quote=(17, "exact slide words"),       # or a list of them; "…" joins pieces of one line
     why="≤ 30 words, plain", tricky=True)  # an AI-written multiple-choice question
dict(q="What is the device-status table?", answer="**…** list or short lines")
                                            # a written question: writing box + Show the answer
```

- The right answer is written first, and the build shuffles the options with a fixed seed. "All of the above" and "none of the above" stay last.
- An item that names only a past or bank id picks up its fixes from `notes.py`. The item's own keys win over the notes.

## What the build stops on

- A concept of a built unit is on no section.
- A past question is placed zero times or twice.
- An AI-written question repeats another.
- A `quote` is not on that slide of the unit (checked against `slides.json` and the concept map).
- An item has neither a `quote` nor a `why`, or its `why` runs past 30 words.
- An AI-written item is true/false.
- A section's `say` names a line that no card shows.

These flags print reports instead of stopping:

- `--cover` lists slide lines that no card covers.
- `--missing` lists narrated lines whose spoken form still holds symbols.

## Read-along

- **Read aloud:** each section's title and its card. That covers paragraphs, list items, terms, tables row by row, and Gantt charts and formula figures by their spoken form.
- **Silent:** questions, tags, slide labels, code (and a heading that only introduces code) and `~>` notes.
- **Spoken text:** every card line carries class `say` and its spoken text in `data-say`. A section's `say` maps a line's plain text to a spoken form wherever the symbols need words.
- **The SS-only switch** marks hidden sections with `data-ra-off`, and the shared player skips them. The audio then reads only what is shown: on IT241, 116 of 1,057 lines.
- **Order of steps:** after `build.py` and `dark-mode.py`, run the read-along skill's `plan`, `status`, `voice`, `render` and `publish`. Never rebuild after `publish`, or the player is dropped.

## Size, for scale

IT241's guide covered Modules 1–5 in 100 sections. It had 831 questions, about 108 minutes of audio and 1,057 narrated lines. Building it took about two days, including one full restart (v1 to v2).
