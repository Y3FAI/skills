# Skills

My own agent skills, kept in sync and published in the public repo **github.com/Y3FAI/skills**. Each folder has a `SKILL.md` that an agent loads and follows. Some also have `tools/` and `reference/`.

Skills published by other people are **not copied here**. Install them from their source so they keep getting updates. **[external.md](external.md)** lists the ones I use and where each comes from.

| Skill | What it does | Needs |
|---|---|---|
| `read-along/` | Narrated audio with word highlighting for a study page: local Kokoro voice, Whisper and Deepgram checks, MP3 and timings on R2 (`media.y3f.me`) | `read-along/tools/setup.sh` (venv at `~/.cache/read-along/venv`), ffmpeg, logged-in `wrangler` |
| `flooki-exam/` | Checked practice exams published on flooki.app, returning the exam link | Python 3 stdlib, token in `~/.config/flooki/token` |
| `browser-use/` | Drive a live Chrome through chrome-devtools-mcp | the chrome-devtools-mcp server |

## Restore on a machine

```sh
git clone https://github.com/Y3FAI/skills ~/sync/skills
bash ~/sync/skills/link.sh                      # links every skill into ~/.claude/skills, ~/.agents/skills, ~/.pi/agent/skills
bash ~/sync/skills/read-along/tools/setup.sh    # voice env for read-along
# Flooki token, once, from the clipboard (never paste it into a chat):
mkdir -p ~/.config/flooki && pbpaste > ~/.config/flooki/token && chmod 600 ~/.config/flooki/token
```

Then install the skills in `external.md` from their sources.

## Rules

- Only my own skills go in this repo. For anyone else's skill, add a line to `external.md`.
- **This repo is public: no secrets and no personal data.** That means no tokens, account IDs, student IDs, grades or schedule files. Tokens live in `~/.config/<tool>/` or in env vars. Never print them.
- After changing a skill, commit and push from `~/sync/skills`.
- Other agents (not Claude Code) should read `<skill>/SKILL.md` directly and run its tools by full path.
