# Example: IT241 Module 11, File Systems

The reference build: the summary the student approved (live at y3f.me/2026-fall/it241/exam-sheets/module-11/).

| File | What it is |
|---|---|
| `master.md` | The final summary text, organized and written by Gemini, with fix-only changes stitched in. 9 topics; blocks: Key terms, Rules, Written questions, Calculations, Traps. |
| `stitch.py` | How the first fix-only round was applied: it parses Gemini's full answer (`r1.md`), applies `REPLACE`/`WITH` and `ADD TO` entries (`r2.md`), and removes duplicates. Its page-building half is superseded by `build_sheet.py`. Adapt it; don’t treat it as a framework. |
| `build_sheet.py` | `master.md` to the page: markers (`KEYS` holds hand-picked key phrases), spoken forms for read-along (`spoken()`, `WORDS`), empty-block guard, page CSS. |
| `figs.py` | The 11 memory pictures as inline SVG, using the summary's own example numbers. |

These are examples for a page in the y3f layout (paths point at `~/dev/y3f/...`). Copy them into a new unit's work folder and change what that unit needs; a math or physics summary will need a different builder shape.
