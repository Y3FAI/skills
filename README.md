# Skills

Agent skills I wrote, plus a catalogue of the external skills I use. A **skill** is a folder with a `SKILL.md`: front matter (`name`, `description`), then instructions an agent follows. Some skills also have tools and reference docs. Claude Code, `~/.agents`-style agents and Pi all read them.

Repo: **github.com/Y3FAI/skills** (public). On my Mac it lives at `~/sync/skills`.

## For AI agents: start here

1. **Find a skill.** Check [My skills](#my-skills) below. If none fits, search **[external.md](external.md)**: 117 skills by others (Apple Xcode, Android, Expo, Cloudflare, web quality, design, …), each with a one-line description and its source.
2. **Use one of mine.** Read `<skill>/SKILL.md` in full and follow it. Run its scripts by full path, e.g. `python3 ~/sync/skills/flooki-exam/tools/flooki.py check exam.json`. Install what its **Needs** column lists first.
3. **Use an external one.** It may already be installed: check `~/.claude/skills`, `~/.agents/skills`, or the project's `.agents/skills` / `.claude/skills`. If not, install it from the source given in `external.md`. **Don't copy it into this repo.**
4. **Secrets.** Never read, print or commit tokens. A skill that needs a token says where it lives (for example `~/.config/flooki/token`). If the token is missing, ask the user.

## My skills

| Skill | Use it for | Needs |
|---|---|---|
| [`read-along`](read-along/SKILL.md) | Add narrated audio with line-by-line highlighting to an HTML page: local Kokoro voice, math read aloud, MP3 and timings uploaded to R2 | `bash read-along/tools/setup.sh` (venv at `~/.cache/read-along/venv`), ffmpeg, logged-in `wrangler` |
| [`flooki-exam`](flooki-exam/SKILL.md) | Turn past papers, a question bank or slides into a checked practice exam on flooki.app and return the link | Python 3 (standard library only); Flooki token in `~/.config/flooki/token` |
| [`browser-use`](browser-use/SKILL.md) | Drive a real Chrome through chrome-devtools-mcp: DOM, CSS, network, console, performance traces, screenshots, clicking and typing | the chrome-devtools-mcp server configured in the agent |
| [`llm-chapter-assignment`](llm-chapter-assignment/SKILL.md) | Build and grade the end-of-chapter assignment notebook for Raschka's *Build a Large Language Model (From Scratch)*, with an Arabic lab | the book PDFs and `~/learn/llm-from-scratch` (torch, tiktoken, nbformat) |

## Install on a new machine

```sh
git clone https://github.com/Y3FAI/skills ~/sync/skills
bash ~/sync/skills/link.sh        # links every skill into ~/.claude/skills, ~/.agents/skills, ~/.pi/agent/skills
```

Then run each skill's own setup, as listed in **Needs**:

```sh
bash ~/sync/skills/read-along/tools/setup.sh
# Flooki token: copy it, then save it from the clipboard (never paste it into a chat):
mkdir -p ~/.config/flooki && pbpaste > ~/.config/flooki/token && chmod 600 ~/.config/flooki/token
```

Install the external skills you need from `external.md`.

## Layout

```
README.md            this page: index, install, rules
external.md          catalogue of external skills (sources, not copies)
link.sh              links each skill folder into the agents' skill folders
<skill>/SKILL.md     the skill: front matter + instructions
<skill>/README.md    human notes: restore steps, history (some skills)
<skill>/tools/       scripts the skill runs (some skills)
<skill>/reference/   docs the skill reads when needed (some skills)
<skill>/examples/    worked examples (some skills)
```

## Add or change a skill

- **My own skill:**
  1. Create `<name>/SKILL.md` with `name` and a `description` that says when to use it.
  2. Add a row to [My skills](#my-skills) and run `bash link.sh`.
  3. Commit and push from `~/sync/skills`.
- **Someone else's skill:** install it from its source and add a row to `external.md` (name, one line on what it's for, source). Don't vendor it, so it keeps getting updates.
- **Before every push:** this repo is **public**. No tokens, account IDs, student IDs, grades, schedules or other personal data.
