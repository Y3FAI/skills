# The page: markers, pictures, layout

What the student asked for on Module 11, in the order the requests came. The working code is in `examples/it241-module-11/`.

## Layout

- **Dark and calm.** The student asked for a "pure dark" background: `#000`, with neutral grey panels and edges (no navy tint, no dot grid).
- **A wide reading column** (about 940px) and **generous vertical space** between items, blocks and topics.
- **No sticky header.** The topic links sit in the page header and scroll away.
- **No gimmicks the student didn't ask for.** A "Test me" mode that blanked every marker was removed.
- **Readable fonts:** Atkinson Hyperlegible Next for reading, a display face for titles, a monospace face for labels and numbers.
- One section per topic, with its number and title. Block labels (KEY TERMS, RULES…) are small, uppercase, with a coloured dot.

## Markers

- **One meaning per colour.** Module 11 used yellow for the term, green for the answer to say, blue for the result, pink for the trap, and ★ for a past-final question. Put the legend at the top.
- **Soft, full-height highlighting behind the words**, at low opacity, with the text slightly tinted toward the colour. **Never a stroke under the text:** the student said it makes the text hard to read. Bright solid markers with dark ink were too distracting.
- **One key phrase per answer:**
  - rules: the direct answer (cut at the first sentence end, or at a clause such as ", so" when it is long);
  - written answers: the label ("Shared:") or the key phrase of each bullet;
  - choose phrases by hand where a rule picks badly (the Module 11 builder has a `KEYS` list).
- Parenthetical asides inside a marker are lighter.

## Pictures (SVG)

Add a picture wherever it connects things better than words, near the top of its topic, labelled "Picture it" with one caption line. Module 11 had 11:

- shared vs exclusive locks;
- sequential vs direct access;
- raw vs formatted partitions;
- the five directory structures, each tagged with what it fixes or adds;
- chmod 761 as bits;
- the layer stack;
- disk vs memory structures, with two processes pointing to one open-file entry;
- the three allocation methods on one 32-block disk;
- FAT and the two-level index;
- where address 3000 falls;
- the four free-space methods.

Rules that worked:
- **Only add.** Pictures sit beside the text and replace nothing.
- **Use the summary's own example numbers** (mail at block 19, jeep's chain 9 16 1 10 25), so picture, text and calculation all point at the same thing.
- Draw in the marker colours, so the same colour keeps the same meaning.
- Don't draw arrows across labels. A chain drawn over a grid hid the block numbers; a clean strip under the grid (9 → 16 → 1 → 10 → 25 → nil) fixed it.
- Inline SVG with a `viewBox`, `width:100%`, and horizontal scroll inside the figure on phones. Arrowhead markers go in one hidden `<svg><defs>` shared by the whole page.
- Parse every SVG as XML in the build, then screenshot each one and look at it.
- Pictures are silent in the read-along.

## Build checks that caught real problems

- **An empty block.** Removing duplicate traps left a "Traps" heading with nothing under it. Drop empty blocks in the builder.
- **Two `class` attributes** on one element, when narration markup was added to an element that already had a class.
- **The read-along player's dark mode** (`html.ra-dark`) restyles `mark`, `dd` and generic variables such as `--paper`, `--muted` and `--line`. Prefix your CSS variables, scope your rules with an id (`#sheet mark`), force dark mode, and hide the player's light switch on a dark-only page.
