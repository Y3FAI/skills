# flooki-exam

A skill for Claude Code and other agents: turn course material (past papers, a question bank, slides, a formula sheet) into checked practice exams on **flooki.app**, and return the shareable link. See **[SKILL.md](SKILL.md)** for the workflow. The Flooki agent API is in `reference/api.md`.

## Restore on a machine

```sh
git clone https://github.com/Y3FAI/flooki-exam ~/sync/skills/flooki-exam
mkdir -p ~/.claude/skills && ln -sfn ~/sync/skills/flooki-exam ~/.claude/skills/flooki-exam
# token, once, from the clipboard (never paste it into a chat):
mkdir -p ~/.config/flooki && pbpaste > ~/.config/flooki/token && chmod 600 ~/.config/flooki/token
```

`tools/flooki.py` uses only the Python 3.8+ standard library, so nothing needs installing. It reads the token from `$FLOOKI_SERVICE_TOKEN`, then `--env-file FILE`, then `~/.config/flooki/token`. **The token is never stored in this repo.**

## Use

```sh
F=~/sync/skills/flooki-exam/tools/flooki.py
python3 $F check   EXAM.json     # every API rule + warnings (duplicates, open $, answer pattern)
python3 $F shuffle EXAM.json     # seeded option shuffle, in place
python3 $F show    EXAM.json     # read it as a student, key marked
python3 $F payload EXAM.json     # the exact request body, no token needed
python3 $F publish EXAM.json     # → https://flooki.app/exam/<id>, recorded in the file
```

## Layout

```
SKILL.md                    how to use it (agents load this)
tools/flooki.py             check | show | shuffle | payload | publish
reference/api.md            Flooki agent API (POST /api/agent/create-exam)
reference/flooki-prompt.md  Flooki's own question-writing rules (from flooki.app/how-to)
examples/minimal.json       one question of each type
```

## History

The original was built on 2026-10-20 at `~/dev/skills/flooki-exam`. It was never committed and was deleted in early November. On 2026-11-08 it was rebuilt from Claude Code session transcripts:

- **`tools/flooki.py`:** its original write plus 10 edits and one shell patch, replayed in order. The `TRIES` retry lines land on exactly the line numbers that session printed.
- **`SKILL.md`:** its write plus two scripted edits. The intermediate state matches a line the session printed.
- **`examples/minimal.json`:** its write, identical to a later printout.
- **`reference/flooki-prompt.md`:** recovered from a full `cat` printout.
- **`reference/api.md`:** the current Flooki agent manual (`~/sync/uni/flooki.md`). Its first 200 lines match the old copy exactly.

The only change from the original is that `SKILL.md` no longer points to a y3f `.env`, which no longer exists.
