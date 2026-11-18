# Read-along for summaries

Use the `read-along` skill for setup, voicing, rendering and publishing. This page covers what is specific to summaries.

## What is narrated

- Topic titles, block labels, terms and their meanings, rule questions and answers, written questions and their answer lines, calculation steps and traps: everything the student reads, in screen order.
- Pictures, legends and links stay silent.
- **A longer pause after each question** (about 1.1 s) gives the listener a moment to answer first. Use a short pause between a term and its meaning.

## Spoken forms

Generate `data-say` automatically from the text, and only where it differs from what is shown. It says the same words with the symbols spelled out. Forms that worked:

- ÷ × = + − become "divided by", "times", "equals", "plus", "minus". `2^40` becomes "2 to the power 40".
- Parentheses become a short pause (commas). "block(s)" becomes "blocks".
- **Pairs keep their grouping:** "(2, 4), (8, 6)" is read "2, 4; 8, 6". Without this, it came out as "2, 4, 8, 6" and lost its meaning.
- Abbreviations are spelled: F C B, N T F S, Z F S, I O, A C L. Commands are said as words: "make dir", "C H mod", "change group".
- Permission strings are read letter by letter: "rw-" becomes "R W dash", and "rwxr-x---" is split into its three groups.
- Bit strings are read digit by digit: "one one zero zero…".
- File extensions: "(lib, a, so, dll)" becomes "lib, A, S O, D L L". A lone lowercase "a" is read as "uh".
- Variables: "Q1" becomes "Q 1"; "r = 4" becomes "R equals 4".

Read the planned script (`spoken_script.txt`) before voicing. Search it for leftover capitals, single letters and symbols.

## After rendering

Most flagged lines are false alarms. Two recognizers listen, and both trip on:

- homophones: disc/disk, right/write, male/mail, ads/adds;
- compound words: "bit map" heard as "bitmap", "I O" as "IO";
- digit runs merged together;
- a soft first syllable at the start of a line ("Acyclic" heard as "Cyclic").

Check a doubtful word with `voice --say "…"`, which prints the phonemes. If the sound is right, it is a false alarm. Fix only real misreadings, re-voice just those lines, render (only changed lines are re-heard), then `publish --force`.

Rebuilding the page drops the player. Re-run `publish`: if the narration is unchanged, it reuses the MP3.
