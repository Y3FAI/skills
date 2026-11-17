# Skills

Agent skills I wrote, plus a catalogue of the external skills I use. A **skill** is a folder with a `SKILL.md`: front matter (`name`, `description`), then instructions an agent follows. Some skills also have tools and reference docs. Claude Code, `~/.agents`-style agents and Pi all read them.

Repo: **github.com/Y3FAI/skills** (public). On my Mac it lives at `~/sync/skills`.

## For AI agents: start here

1. **Find a skill.** Check [My skills](#my-skills) below. If none fits, search **[external.md](external.md)**: 117 skills by others (Apple Xcode, Android, Expo, Cloudflare, web quality, design, …), each with a one-line description and its source.
2. **Use one of mine.** Read `<skill>/SKILL.md` in full and follow it. Run its scripts by full path, e.g. `python3 ~/sync/skills/flooki-exam/tools/flooki.py check exam.json` (or `.agents/skills/<skill>/…` when the skill is installed in the project). Install what its **Needs** column lists first.
3. **Use an external one.** It may already be installed: check `~/.claude/skills`, `~/.agents/skills`, or the project's `.agents/skills` / `.claude/skills`. If not, install it from the source given in `external.md`. **Don't copy it into this repo.**
4. **Secrets.** Never read, print or commit tokens. A skill that needs a token says where it lives (for example `~/.config/flooki/token`). If the token is missing, ask the user.

## My skills

| Skill | Use it for | Needs |
|---|---|---|
| [`read-along`](read-along/SKILL.md) | Add narrated audio with line-by-line highlighting to an HTML page: local Kokoro voice, math read aloud, MP3 and timings uploaded to R2 | `bash read-along/tools/setup.sh` (venv at `~/.cache/read-along/venv`), ffmpeg, logged-in `wrangler` |
| [`flooki-exam`](flooki-exam/SKILL.md) | Turn past papers, a question bank or slides into a checked practice exam on flooki.app and return the link | Python 3 (standard library only); Flooki token in `~/.config/flooki/token` |
| [`browser-use`](browser-use/SKILL.md) | Drive a real browser: an isolated Chrome through chrome-devtools-mcp (DOM, CSS, network, console, performance, screenshots, clicks), or your own logged-in Zen / Firefox through a WebDriver BiDi driver (dashboards such as Play Console) | chrome-devtools-mcp configured in the agent; for Zen / Firefox: Node and `bash browser-use/tools/setup.sh` |
| [`user-writer-in-browser`](user-writer-in-browser/SKILL.md) | Get user-facing text (legal pages, app copy, website words, Arabic or any language) written by Gemini in your own logged-in browser: the agent gathers and checks the facts, sends a brief, reviews each answer, and sends numbered corrections until it is right | `browser-use` driver on Zen / Firefox; a Gemini login |
| [`exam-study-guide`](exam-study-guide/SKILL.md) | Build an exam study guide from slides, past papers and banks: exam analysis → concept map → SS/S/A/B priorities → micro-sections → cards + exam-pattern questions → read-along. Captures each course's shape (IT241, SCI201, STAT101, MATH251, ENG103) | the course sources (slides, papers, banks); the `read-along` skill for audio |
| [`direct-real-phone-testing`](direct-real-phone-testing/SKILL.md) | Test an Expo / React Native app on your real iPhone and Android phone, never a simulator: Release builds, an XCUITest runner walking journeys by testID with timings, the app's own diagnostics trail, screenshots and full-run recordings, contact sheets, frame gaps, Instruments hitches/hangs, a local test server with fake data. Points to Apple's, Google's and Expo's official skills and keeps them updated | Xcode + `xcodegen`, an iPhone with Developer Mode and UI Automation on; `adb` + JDK 17 for Android; Node, ffmpeg |
| [`expo-native-html-prototype`](expo-native-html-prototype/SKILL.md) | Build native iOS and Android apps in Expo from an HTML prototype: quick design directions, then one working phone prototype (real navigation, swipe and predictive back, sheets with the keyboard, a tile that grows into its screen, iPhone/Android switch, options to compare, slow motion, RTL), the user decides by feel, then each piece is built with the platform's own components and the phone is checked against the prototype | Google Chrome and Node 22 for `tools/shoot.mjs`; Expo's, Google's and Apple's official skills |
| [`project-blueprint`](project-blueprint/SKILL.md) | Set up or reorganise a project the way a well-run app was managed: AGENTS.md (read order, decisions, map, commands, rules, done), docs/ as the build contract (gated plan, one-page decision log, ADRs, product, architecture, testing, security, operations), research apart from decisions, a playground for HTML design, per-project skills, one CI gate, docs updated with the code. A scaffold that never overwrites | bash, perl (macOS default) |
| [`llm-chapter-assignment`](llm-chapter-assignment/SKILL.md) | Build and grade the end-of-chapter assignment notebook for Raschka's *Build a Large Language Model (From Scratch)*, with an Arabic lab | the book PDFs and `~/learn/llm-from-scratch` (torch, tiktoken, nbformat) |

**Building an app:** three skills work as a set. Use `project-blueprint` to organise the repo and its docs, `expo-native-html-prototype` to design in HTML and build each platform natively, and `direct-real-phone-testing` to verify on the real phones. Each points to the official Apple, Google and Expo skills for the details.

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

**Into one project** (how app projects get skills: the repo carries them, any agent finds them):

```sh
npx skills@latest add Y3FAI/skills -a universal claude-code -y -s project-blueprint expo-native-html-prototype direct-real-phone-testing
npx skills@latest update -p    # later: refresh the project's skills, mine and the official ones
```

This writes `.agents/skills/<name>` plus `.claude/skills` links and records them in the project's `skills-lock.json`. `npx skills add Y3FAI/skills -l` lists what's available.

## Layout

```
README.md            this page: index, install, rules
external.md          catalogue of external skills (sources, not copies)
link.sh              links each skill folder into the agents' skill folders
<skill>/SKILL.md     the skill: front matter + instructions
<skill>/README.md    human notes: restore steps, history (some skills)
<skill>/tools/       scripts the skill runs (some skills)
<skill>/reference/   docs the skill reads when needed (some skills)
<skill>/templates/   files the skill copies into a project (some skills)
<skill>/examples/    worked examples (some skills)
```

## Add or change a skill

- **My own skill:**
  1. Create `<name>/SKILL.md` with `name` and a `description` that says when to use it.
  2. Add a row to [My skills](#my-skills) and run `bash link.sh`.
  3. Commit and push from `~/sync/skills`.
- **Someone else's skill:** install it from its source and add a row to `external.md` (name, one line on what it's for, source). Don't vendor it, so it keeps getting updates.
- **Before every push:** this repo is **public**. No tokens, account IDs, student IDs, grades, schedules or other personal data.
