---
name: read-along
description: Add read-along audio to an HTML page. A Kokoro voice (free, runs locally) narrates chosen elements, and the page highlights each line as it is spoken; tap any line to jump there. Use when asked to add narration, audio notes, text-to-speech, "read along" or a listen mode to a web page or study guide, especially pages with math formulas.
---

# Read-along: Kokoro narration with synced highlighting

The result is the same page plus a docked audio player. Each narrated line highlights while it is spoken, the page scrolls along, tapping a line plays from it, headings become chapters, and a light switch adds dark mode. The page content is never edited. `publish` only inserts two blocks between `<!-- READ-ALONG:START/END -->` markers and can remove them again.

It is proven on the y3f study guides: SCI201 physics, ENG103, and a 59-minute MATH251 guide with about 600 lines of linear algebra.

## Folder map

```
read-along/
  SKILL.md                 this file
  tools/setup.sh           one-time: venv with Kokoro + BeautifulSoup + spaCy model
  tools/readalong.py       the pipeline: plan | status | voice | render | publish | strip
  assets/read-along.js     the player (highlighting, seeking, chapters, dark mode)
  assets/read-along.css
  examples/minimal/        a tiny page + readalong.json; start by copying these
  reference/spoken-math.md how to write formulas for the ear (examples that worked)
```

## 1. Setup (once per machine)

```sh
bash tools/setup.sh                      # venv at ~/.cache/read-along/venv
PY=~/.cache/read-along/venv/bin/python   # use this python for every command below
```

It needs `uv`, plus `ffmpeg`/`ffprobe` on PATH. For Whisper checks or R2 uploads it also needs Node with a logged-in `npx wrangler`.

**Slow first start on macOS:** right after setup, the first `import torch` can take 10–15 minutes while macOS scans the new libraries, and any other run started meanwhile waits too. Start one run and let it finish. After that, startup takes about 2 seconds.

## 2. Mark up the page

- Give every element that should be read `class="say"` (or set your own `selector`). Leave everything else unmarked: quizzes, tags, sources and navigation stay silent.
- **`data-say="..."`** is what the voice says for that element, as one line. Use it whenever the element shows math, symbols, abbreviations or anything that reads badly. Without `data-say`, the element's visible text is split into sentences and read as shown.
- **`data-role`** (optional) sets the pause after the line: `equation` 700 ms, `question` 650, `step` 480, `body` 320, `term` 150, `label` 250. h1/h2/h3+ get title/heading/subheading pauses automatically.
- **`data-box="..."`** (optional) on a wrapper adds a longer 950 ms pause when the narration moves into the next box, for example from rule to explanation to example.
- **Chapters:** each narrated `h2` starts a chapter in the player. Lines are grouped by the nearest ancestor matching `section` (CSS, default `section`).
- Don't nest `.say` elements. With `leaf: true`, an element holding other matches is skipped.
- The page needs `</head>` and `</body>`. KaTeX math is fine: the player highlights a whole formula as one block.

## 3. Write what the voice says (this is where quality comes from)

- **No symbols ever reach the voice.** `plan` rejects any line containing `= + / ^ _ ( ) [ ] < > × − · √ …`, so write them in words.
- **Say formulas by meaning, not symbol by symbol.** "Subtract matching coordinates, square each difference, add them, then take the square root" beats "square root of open paren u one minus v one…".
- Use **one spoken form per notation** throughout, for example "A transpose", "A inverse", "u dot v", "the norm of u", "R 3", "2 by 3".
- **Matrices:** "rows 1, 2 and 3, 4" for small ones. Describe big ones by their shape.
- **Variables named `a`:** write them as capital `A` in `data-say`. Kokoro reads lowercase "a" as the article "uh". With `letter_a: true` (the default), the local voice also forces a lone capital A to sound like the letter, except at the start of a sentence followed by an ordinary word or number ("A matrix is…", "A 2 by 2…").
- **Keep lines short.** Sentences over 260 characters are split for highlighting. Give very short headings a few words of context ("The subspace test." rather than "Subspace Test"), or the checks mishear them.
- **Narrate content only.** Don't voice provenance ("this came from the exam"), tags or quiz questions unless the user asks.
- **Say what is on screen, in screen order.** A `data-say` only turns math and symbols into words. It never swaps in a rewritten sentence, so listeners can follow along. For true-or-false lists, use one line for the statement and one for "True." or "False." plus the reason. Show them in that same order too (statement first, then the verdict badge on the reason line).
- **Don't end a line on a lone letter** ("…d equals delta V over E."). The checkers can miss the final letter. End on a word, for example "…over E, not E times delta V."
- Check any doubtful sentence with: `$PY tools/readalong.py CONFIG voice --say "A inverse is one over A d minus b c."` It prints the phonemes; `ˈA` is the letter and `ɐ` is "uh".

See `reference/spoken-math.md` for worked examples.

## 4. Config: `readalong.json` next to the page

```json
{
  "page": "index.html",
  "slug": "my-guide",
  "selector": ".say",
  "root": "main",
  "section": "section",
  "artist": "Course name",
  "album": "Study guides",
  "tts": "local",
  "verify": "auto",
  "publish": {"mode": "local", "folder": "audio"},
  "player": "copy"
}
```

- **`tts`:** `local` uses Kokoro on this machine (free). `openrouter` uses the same model through the API; set `OPENROUTER_API_KEY` or pass `--env-file FILE`.
- **`verify`:** `cloudflare` runs Whisper, with a second opinion from Deepgram Nova, on Workers AI, and needs `cloudflare_account` (or `CLOUDFLARE_ACCOUNT_ID`) plus a wrangler login or `CLOUDFLARE_API_TOKEN`. `none` skips checking. `auto` checks only when an account id is set.
- **`publish`:**
  - `{"mode": "local"}` writes the MP3 into `folder` next to the page and links it relatively.
  - `{"mode": "r2", "bucket": "...", "public_url": "https://media.example.com", "prefix": "course"}` uploads it with wrangler and checks that HTTP range requests work. The file name is content-addressed, so new audio never collides with a cached old file.
- **`player`:** `copy` places the skill's player in `read-along/` next to the page. Otherwise give a folder that already serves `read-along.js`/`.css` (y3f uses `../../../assets`).
- **Optional:**
  - `pauses` overrides pause lengths in ms.
  - `speech` maps an exact visible sentence to a spoken form, for text you can't give a `data-say`.
  - `title` sets the MP3 title.
  - `recheck` (`changed` by default, or `all` / `none`) and `spot_checks` (12) control how many lines are re-heard out of the finished MP3.
  - `mp3_quality` is the LAME `-q` setting. The default 2 encodes a 2-hour file in about a minute; 0 is about 3× slower, with the same size and timing and no audible gain for speech.

Clips and transcripts are cached in `~/.cache/read-along/<slug>/`, so only changed lines are ever voiced or transcribed again.

## 5. Run

```sh
$PY tools/readalong.py CONFIG plan       # page → spoken_script.txt; fails on symbols. READ the script.
$PY tools/readalong.py CONFIG status     # what changed since the last render; what voice/render/publish still need
$PY tools/readalong.py CONFIG voice      # local Kokoro, about 1–2 s per line, only lines without a clip; --all redoes all
$PY tools/readalong.py CONFIG render     # MP3: edge-trimmed clips, planned pauses, loudness, checks
$PY tools/readalong.py CONFIG publish    # MP3 out + player in; --force if only false alarms remain
$PY tools/readalong.py CONFIG strip      # take the player off the page again
```

`render` options:

| Option | What it does |
|---|---|
| (default) | Re-hears only new or changed lines out of the finished MP3, plus 12 evenly spaced spot checks that would catch timing drift. Every other line keeps its transcript from the last render, scored again with the current matcher. |
| `--recheck all` | Re-hears every line. Use it for a first render or after changing pauses. |
| `--recheck none` | Re-hears nothing. Changed lines then have no MP3 transcript until the next render. |
| `--spot N` | Changes the number of spot checks. |
| `--no-verify` | No Whisper or Nova at all: a quick draft MP3. |
| `--preview 40-60,75` or `--preview "some text"` | Only those lines (numbers as in `status`/`report.json`) go into `preview.mp3`, in seconds, so you can listen to a fix. The real MP3, timeline and report don't change. |

- **After `plan`:** run `status` to see exactly which lines are new, then read `~/.cache/read-along/<slug>/spoken_script.txt` as if listening. That is where wrong wording is cheap to fix.
- **After `render`:** read `report.json`. Check `duration`, `whisper_mean` (0.98 or higher is good), `render_seconds`, and `problems`.
  - The matcher already treats these as equal: spelled-out and digit numbers ("thirty-six" = 36, "ten thousand" = 10,000), trailing zeros (0.50 = 0.5), UK/US spellings (metre/meter), and letters heard as words ("cue" = q, "are" = r, "naught"/"nought" = 0). So what remains is usually real.
  - If both recognizers wrote a homophone, it's a false alarm; publish with `--force`. Examples: "Cramer" heard as "Kramer", "there's" for "there is".
  - Anything else means the voice said it wrong: reword the `data-say`, run `voice`, check it with `render --preview "…"`, then `render`.
- **Timing (a 160-minute, 1,342-line guide on an M-series Mac):** `voice` takes 1–2 s per new line. `render` takes about 2 minutes: around 60 s is the MP3 encode, and the rest is mastering, true-peak checks and the network calls for changed lines. A render that re-hears every line (`--recheck all`) takes 20–30 minutes, so run that one in the background.

## 6. Check it in a browser

Serve the folder over HTTP (`python3 -m http.server`), not `file://`, because seeking needs range requests. Then confirm:

- The player docks at the bottom with the right duration.
- The console shows no "block(s) changed since the audio was built" warning. If it does, the page changed after `render`, so render again.
- Tapping a line plays from it, and formulas highlight as whole blocks.

## 7. Changing the page later

- Any rebuild of the page (by your generator) drops the player. Re-run `publish`. If the narrated text is unchanged, it reuses the existing MP3.
- `publish` refuses to run when the narration or the line offsets changed since `render`. Run `plan`, `status`, `voice`, `render` and `publish` again. Only new lines get voiced, only new clips get transcribed, and only changed lines get re-heard out of the MP3. A one-line fix takes a few minutes from start to finish.
- Never hand-edit between the READ-ALONG markers.

## Pitfalls learned the hard way

- **Network flakes:** the network calls (OpenRouter, Workers AI, R2) retry with backoff. If a run dies with "Network is unreachable", just re-run it: everything finished so far is cached.
- **Expired Cloudflare login:** `render` checks the login before the long work and stops in seconds with "no Cloudflare token from wrangler". The user runs `npx wrangler login` (interactive; in Claude Code, `! npx wrangler login`). Until then, `render --no-verify` still builds the MP3, and `--recheck none` works when every clip transcript is cached. Never print `wrangler auth token` output: it's a credential.
- **OpenRouter credits:** when they run out, the API answers HTTP 402. Switch to `"tts": "local"`. It's the same model and voice, and the cache keys match.
- **Hugging Face hangs:** once the weights are cached, the tool runs with `HF_HUB_OFFLINE=1`. Online checks used to hang whole runs.
- **R2 404s:** probe a new URL only with a throwaway query string, or the CDN caches a 404 for hours. `put_audio` does this.
- **Stray `.wrangler/` folder:** wrangler writes `.wrangler/` into the folder it runs from. The tool runs it from the cache dir; if you run wrangler yourself, don't commit that folder.
- **Copy-paste:** text copied from a KaTeX page comes out doubled ("a32a32"), because the hidden MathML copy is included. That's normal; what's on screen is fine.
- **Short fragments:** "Solve:" or "Cofactor:" alone can come out unclear. Merge them with the next line, or add context.
