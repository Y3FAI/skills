# read-along

A skill for Claude Code and other agents: Kokoro narration for HTML pages, with each line highlighted as it is spoken, tap-to-seek, chapters and dark mode. It powers the read-along audio on the y3f.me study guides. See **[SKILL.md](SKILL.md)** for the full workflow.

## Restore on a machine (or after anything gets deleted)

```sh
git clone https://github.com/Y3FAI/read-along ~/dev/read-along
mkdir -p ~/.claude/skills && ln -sfn ~/dev/read-along ~/.claude/skills/read-along
bash ~/dev/read-along/tools/setup.sh      # voice env: ~/.cache/read-along/venv (Kokoro, bs4, spaCy model)
```

The repo holds only source. `setup.sh` recreates everything else: the venv (~1 GB with PyTorch) and the ~330 MB Kokoro weights. Audio caches live in `~/.cache/read-along/<slug>/` and can be deleted at any time.

Older y3f pages have their own `build-audio.py` and `tools/kokoro_local.py`, which expect `~/.cache/y3f-readalong/kokoro-venv`. Point that path at the same venv:
```sh
mkdir -p ~/.cache/y3f-readalong && ln -sfn ~/.cache/read-along/venv ~/.cache/y3f-readalong/kokoro-venv
```

**Needs:** [`uv`](https://docs.astral.sh/uv/), `ffmpeg`/`ffprobe`.
- Whisper/Nova checks and R2 uploads also need Node with a logged-in `npx wrangler`.
- `"tts": "openrouter"` also needs `OPENROUTER_API_KEY`, or pass `--env-file`.

## Smoke test

```sh
PY=~/.cache/read-along/venv/bin/python
cp -R ~/dev/read-along/examples/minimal /tmp/ra-test && cd /tmp/ra-test
$PY ~/dev/read-along/tools/readalong.py readalong.json plan
$PY ~/dev/read-along/tools/readalong.py readalong.json voice
$PY ~/dev/read-along/tools/readalong.py readalong.json render
$PY ~/dev/read-along/tools/readalong.py readalong.json publish
python3 -m http.server      # open http://localhost:8000 and press play
```

## Layout

```
SKILL.md                 how to use it (agents load this)
tools/setup.sh           one-time voice environment
tools/readalong.py       plan | status | voice | render | publish | strip
assets/read-along.js     the player: highlighting, seeking, chapters, dark mode
assets/read-along.css
examples/minimal/        a tiny page + readalong.json to copy
reference/spoken-math.md how to write formulas for the ear
```

## History

The original was built in October 2026 at `~/dev/skills/read-along` and was never committed. It was deleted in early November. On 2026-11-08 it was rebuilt from Claude Code session transcripts:

- **`tools/readalong.py`:** stitched from five chunked reads of the 2026-10-20 version (lines 1–1049). The 30 later edits were then replayed, and the result matches all 7 later partial reads exactly.
- **`SKILL.md`:** the 2026-10-20 full read plus its 6 later edits. That read is identical to the original write.
- **`setup.sh`, `reference/`, `examples/`:** their original writes.
- **`assets/`:** copied from the deployed y3f.me player, which already includes the skill's last player edits.

This repo exists so it never has to be rebuilt that way again.
