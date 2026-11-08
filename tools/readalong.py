#!/usr/bin/env python3
"""read-along: narrate an HTML page with Kokoro and make every narrated line highlight and seek.

    python readalong.py CONFIG plan      # page → spoken script + checks (no audio)
    python readalong.py CONFIG status    # what changed since the last render, what still needs voice/render/publish
    python readalong.py CONFIG voice     # voice every line on this machine with Kokoro (needs the venv)
    python readalong.py CONFIG render    # clips → verified, rhythm-timed, loudness-matched CBR MP3
    python readalong.py CONFIG render --preview 40-60   # just those lines → preview.mp3, to listen to a fix
    python readalong.py CONFIG publish   # MP3 → R2 or next to the page; player + timeline → the page

CONFIG is a JSON file (see SKILL.md and examples/minimal/readalong.json); paths in it are relative
to the config file. The page is the source of truth and its content is never edited: publish only
(re)writes two blocks between READ-ALONG markers (one before </head>, one before </body>).

What the voice says: every element matched by "selector" inside "root" is one block. An element
with data-say is spoken as that text (one line); otherwise its text is split into sentences.
Spoken text must hold no symbols: write math and notation in words in data-say.

Pipeline (from the y3f SCI201 / ENG103 / MATH251 study guides):
  - voice: Kokoro 82M "af_heart", locally (voice) or on OpenRouter (render calls it for missing clips)
  - post: lossless PCM clips, edge silence normalised so every gap is the planned pause, per-clip
    checks, optional Whisper + Nova round-trip on Cloudflare Workers AI, loudness match, CBR MP3,
    and a final pass that re-hears lines out of the finished MP3 at their timeline slots: by default
    only new or changed lines plus a few spot checks (--recheck all re-hears every line).
"""
from __future__ import annotations

import argparse
import array
import base64
import difflib
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except ImportError:  # pragma: no cover
    raise SystemExit("error: needs beautifulsoup4 (run tools/setup.sh, then use its venv's python)")
try:   # the venv has it (Kokoro needs it); sample loops fall back to plain Python without it
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

SKILL = Path(__file__).resolve().parent.parent
START, END = "<!-- READ-ALONG:START -->", "<!-- READ-ALONG:END -->"

# ---- config -------------------------------------------------------------------
DEFAULTS = {
    "page": "index.html",
    "slug": None,                       # cache folder + MP3 name; default: the page folder's name
    "selector": ".say",                 # narrated elements (the player uses the same selector)
    "root": "body",                     # only elements inside this are read
    "section": "section",               # chapters: each heading starts one; lines inside count to it
    "leaf": True,                       # an element holding other matches is not a line itself
    "title": None,                      # MP3 title; default: <h1 data-say> or <title>
    "artist": "",
    "album": "",
    "voice": "af_heart",
    "tts": "local",                     # "local" (Kokoro on this machine) or "openrouter"
    "letter_a": True,                   # say a lone capital A as the letter, not the article "uh"
    "verify": "auto",                   # "cloudflare", "none", or "auto" (cloudflare when an account is set)
    "recheck": "changed",               # MP3 re-hearing: "changed" (new/changed lines + spot checks), "all", "none"
    "spot_checks": 12,                  # unchanged lines re-heard out of the MP3 to confirm the timing still holds
    "mp3_quality": 2,                   # LAME -q: 2 = near-best (a 2-hour file in ~1 min); 0 = ~3x slower, same size
    "cloudflare_account": None,         # or env CLOUDFLARE_ACCOUNT_ID
    "publish": {"mode": "local"},       # {"mode": "local"} or {"mode": "r2", "bucket", "public_url", "prefix"}
    "player": "copy",                   # "copy" (skill's assets next to the page) or a folder with read-along.js/.css
    "pauses": {},                       # override PAUSE entries, in ms
    "speech": {},                       # exact visible sentence → spoken form (rare fixes)
}
PAUSE = {"title": 900, "label": 250, "heading": 650, "subheading": 650, "term": 150, "body": 320,
         "equation": 700, "question": 650, "step": 480}
BOX_END_PAUSE = 950      # when the next line sits in another [data-box] (rule → explanation → example)
SENTENCE_PAUSE = 0
SECTION_END_PAUSE = 760  # before any heading: replaces, never stacks
HEADINGS = {"title", "label", "heading", "subheading"}
LONG_LINE = 260  # longer sentences are split at a clause into two lines
CFG: dict = {}
PAGE = WORK = Path(".")
SLUG = ""


def load_config(path: str) -> None:
    global CFG, PAGE, WORK, SLUG
    cfg_path = Path(path).resolve()
    CFG = {**DEFAULTS, **json.loads(cfg_path.read_text(encoding="utf-8"))}
    PAGE = (cfg_path.parent / CFG["page"]).resolve()
    if not PAGE.exists():
        raise SystemExit(f"error: no page at {PAGE}")
    SLUG = CFG["slug"] or re.sub(r"[^a-z0-9-]+", "-", PAGE.parent.name.lower()).strip("-") or "read-along"
    WORK = Path(os.environ.get("READALONG_WORK", Path.home() / ".cache" / "read-along" / SLUG))
    PAUSE.update(CFG["pauses"])


# ---- speech text ---------------------------------------------------------------
ACRONYMS: list[tuple[str, str]] = []   # applied before capitals are lowered: (regex, spoken)
TERMS = [
    (r"\be\.g\.,?", "for example,"), (r"\bi\.e\.,?", "that is,"), (r"\betc\.", "and so on"),
    (r"\bvs\.?(?=\s)", "versus"), (r"\band/or\b", "and or"),
    (r"(?<=[A-Za-z])/(?=[A-Za-z])", " or "), (r"\s+—\s+", ", "), (r"—", ", "),
]
# Nothing that reaches the voice may contain these: symbols Kokoro would read out or mangle.
SPOKEN_SYMBOLS = re.compile(r"[⟦⟧$\\^_{}/()\[\]<>=*+`|~→↔·–−—×≈°±∞§•]")
ABBREVIATIONS = re.compile(r"\b(?:e\.g|i\.e|etc|vs|cf|Mr|Ms|Mrs|Dr)\.$")


def speak(text: str, **_: object) -> str:
    """Visible sentence (or data-say) → what the voice says."""
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("“", "").replace("”", "").replace("’", "'").replace("‘", "'").replace("…", "...")
    text = re.sub(r"(\d[\d,.]*)\s*–\s*(\d[\d,.]*)", r"\1 to \2", text)
    text = re.sub(r"(?<=\w)[–-](?=\w)", "-", text)
    text = re.sub(r"_{2,}", "blank", text)
    text = re.sub(r"\s*\(([^()]+)\)", r", \1,", text)
    text = text.replace(" · ", ", ").replace("&", " and ").replace("•", "")
    for pattern, replacement in ACRONYMS:
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"\b[A-Z]{3,}\b", lambda m: m.group().lower(), text)   # NOT, ONLY: emphasis, not acronyms
    for pattern, replacement in TERMS:
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"(^|:\s)\.{3,}\s*", lambda m: m.group(1) + "Blank ", text)
    text = re.sub(r"\s*\.{3,}\.?", " blank.", text)
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)
    text = re.sub(r"([.;:!?])\s*[,.]", r"\1", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip().rstrip(",").strip()
    if text and text[-1] not in ".!?:;":
        text += "."
    return CFG["speech"].get(text, text)


# ---- extraction ---------------------------------------------------------------


def original_html() -> str:
    """The page without the injected read-along blocks (= the untouched page)."""
    html = PAGE.read_text(encoding="utf-8")
    return re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", html, flags=re.S)


def is_math(node: Tag) -> bool:
    return "katex" in (node.get("class") or []) and node.find_parent(class_="katex") is None


def block_text(el: Tag) -> tuple[str, str, list[int]]:
    """(textContent, readable text, map). The readable text swaps each formula's rendered
    characters for ⟦TeX⟧; map[i] is the textContent offset of readable offset i, so a
    sentence found in the readable text highlights exactly the right characters."""
    raw: list[str] = []
    clean: list[str] = []
    cmap: list[int] = []
    pos = 0

    def walk(node: Tag) -> None:
        nonlocal pos
        for child in node.children:
            if isinstance(child, Tag):
                if "tags" in (child.get("class") or []):   # red "asked in" chips: shown, never read
                    text = child.get_text()
                    raw.append(text)
                    pos += len(text)
                elif is_math(child):
                    rendered = "".join(str(t) for t in child.descendants
                                       if isinstance(t, NavigableString) and type(t) is NavigableString)
                    tex = child.select_one('annotation[encoding="application/x-tex"]').get_text().strip()
                    token = f"⟦{tex}⟧"
                    raw.append(rendered)
                    clean.append(token)
                    cmap.extend([pos] * len(token))
                    pos += len(rendered)
                else:
                    walk(child)
            elif type(child) is NavigableString:
                text = str(child)
                raw.append(text)
                clean.append(text)
                cmap.extend(range(pos, pos + len(text)))
                pos += len(text)

    walk(el)
    cmap.append(pos)
    return "".join(raw), "".join(clean), cmap


def js_len(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def sentence_spans(text: str, breaks: list[int]) -> list[tuple[int, int]]:
    """[start, end) spans of each sentence (Python indices), trimmed of whitespace."""
    cuts = {0, len(text), *breaks}
    for m in re.finditer(r"[.!?][”\"’)]*(?=\s+\S)", text):
        if re.match(r"\s+[a-z]", text[m.end():]):
            continue
        if not ABBREVIATIONS.search(text[: m.end()]) and not re.fullmatch(r"\s*\d+\.", text[: m.end()]):
            cuts.add(m.end())
    points = sorted(cuts)
    spans = []
    for a, b in zip(points, points[1:]):
        while a < b and text[a].isspace():
            a += 1
        while b > a and text[b - 1].isspace():
            b -= 1
        if b > a:
            spans.extend(split_long(text, a, b))
    return spans


def split_long(text: str, a: int, b: int) -> list[tuple[int, int]]:
    """A sentence over LONG_LINE characters becomes two lines at the clause nearest
    its middle (semicolon first, then colon, then comma)."""
    if b - a <= LONG_LINE:
        return [(a, b)]
    mid = (a + b) // 2
    for mark in ("; ", ": ", ", "):
        options = [m.start() + 1 for m in re.finditer(re.escape(mark), text[a:b])]
        options = [a + o for o in options if 60 < o < (b - a) - 60]
        if options:
            cut = min(options, key=lambda o: abs(o - mid))
            rest = cut
            while rest < b and text[rest].isspace():
                rest += 1
            return split_long(text, a, cut) + split_long(text, rest, b)
    return [(a, b)]


def role_of(el: Tag) -> str:
    """h1 title, h2 heading, h3–h6 subheading, else body; data-role on the element overrides
    (equation, question, step, label, term, body): math and steps get a longer pause."""
    if el.get("data-role") in PAUSE:
        return el["data-role"]
    if el.name == "h1":
        return "title"
    if el.name == "h2":
        return "heading"
    if el.name in ("h3", "h4", "h5", "h6"):
        return "subheading"
    return "body"


def box_of(el: Tag) -> str:
    """The nearest [data-box] around a line: a longer pause marks the move from one box to the next."""
    box = el if el.get("data-box") else el.find_parent(attrs={"data-box": True})
    return f"{box.get('data-box')}#{id(box)}" if box is not None else ""


def plan_lines() -> tuple[list[dict], list[dict]]:
    soup = BeautifulSoup(original_html(), "html.parser")
    main = soup.select_one(CFG["root"])
    if main is None:
        raise SystemExit(f"error: root {CFG['root']!r} matches nothing in {PAGE.name}")
    elements = main.select(CFG["selector"])
    if not elements:
        raise SystemExit(f"error: selector {CFG['selector']!r} matches nothing inside {CFG['root']!r}")
    if CFG["leaf"]:
        chosen = set(map(id, elements))
        elements = [el for el in elements if not any(id(d) in chosen for d in el.find_all(True))]
    order = {id(sec): n for n, sec in enumerate(main.select(CFG["section"]), 1)}
    blocks, lines = [], []
    for bi, el in enumerate(elements):
        raw, clean, cmap = block_text(el)
        role = role_of(el)
        sec_index = next((order[id(p)] for p in el.parents if id(p) in order), 0)
        blocks.append({"b": bi, "tag": el.name, "role": role, "len": js_len(raw),
                       "text": re.sub(r"\s+", " ", clean).strip()})
        whole = (len(clean) - len(clean.lstrip()), len(clean.rstrip()))
        if el.get("data-say") or role in HEADINGS:
            spans = [whole]
        else:
            spans = sentence_spans(clean, [])
        for a, b in spans:
            shown = re.sub(r"\s+", " ", clean[a:b]).strip()
            said = speak(el["data-say"]) if el.get("data-say") else speak(shown)
            if not said:
                continue
            ra, rb = cmap[a], cmap[b]
            lines.append({
                "i": len(lines), "b": bi, "role": role, "section": sec_index,
                # UTF-16 offsets into the element's textContent: what the browser's DOM uses.
                "s": js_len(raw[:ra]), "e": js_len(raw[:rb]),
                "shown": shown, "text": said, "lastInBlock": True, "box": box_of(el),
                "hold": int(el["data-pause"]) if el.get("data-pause") else 0,   # thinking time after a question
            })
            if len(lines) > 1 and lines[-2]["b"] == bi:
                lines[-2]["lastInBlock"] = False
    for n, line in enumerate(lines):
        nxt = lines[n + 1] if n + 1 < len(lines) else None
        if not line["lastInBlock"]:
            pause = SENTENCE_PAUSE
        else:
            pause = PAUSE[line["role"]]
            if (nxt is None or nxt["role"] in HEADINGS) and line["role"] not in HEADINGS:
                pause = max(pause, SECTION_END_PAUSE)
            elif nxt is not None and nxt["box"] != line["box"] and line["role"] not in HEADINGS:
                pause = max(pause, BOX_END_PAUSE)
        if line["hold"] and line["lastInBlock"]:
            pause = line["hold"]
        line["pause"] = pause
    return blocks, lines


def check_lines(lines: list[dict]) -> list[str]:
    errors = []
    for line in lines:
        if SPOKEN_SYMBOLS.search(line["text"]):
            errors.append(f"line {line['i']} still has a symbol: {line['text']!r}")
        if not re.search(r"[A-Za-z]", line["text"]):
            errors.append(f"line {line['i']} has nothing to say: {line['shown']!r}")
    return errors


def cmd_plan(_: argparse.Namespace) -> int:
    blocks, lines = plan_lines()
    errors = check_lines(lines)
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "plan.json").write_text(json.dumps({"blocks": blocks, "lines": lines}, indent=1, ensure_ascii=False))
    script = []
    for line in lines:
        script.append(line["text"])
        script.append(f"[pause {line['pause']}ms]")
    (WORK / "spoken_script.txt").write_text("\n".join(script) + "\n")
    longest = max(lines, key=lambda x: len(x["text"]))
    print(f"plan: {len(blocks)} blocks, {len(lines)} lines, {sum(len(x['text'].split()) for x in lines)} words; "
          f"longest line {len(longest['text'])} chars")
    print(f"wrote {WORK / 'plan.json'} and {WORK / 'spoken_script.txt'}")
    for e in errors:
        print("error:", e, file=sys.stderr)
    return 1 if errors else 0


# ---- voice + ears ---------------------------------------------------------------

MODEL, SR = "hexgrad/kokoro-82m", 24000  # the voice is CFG["voice"] (default af_heart)
WRANGLER_CONFIG = Path.home() / "Library" / "Preferences" / ".wrangler" / "config" / "default.toml"
WORKERS = 8  # same request concurrency as the existing SCI201 pipeline




def cf_account() -> str:
    account = CFG.get("cloudflare_account") or os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if not account:
        raise SystemExit("error: verify needs a Cloudflare account id (config cloudflare_account or CLOUDFLARE_ACCOUNT_ID)")
    return account


def verifying() -> bool:
    mode = CFG["verify"]
    if mode == "auto":
        return bool(CFG.get("cloudflare_account") or os.environ.get("CLOUDFLARE_ACCOUNT_ID"))
    return mode == "cloudflare"


# Prefer IPv4: on a flaky IPv6 route half the TLS sessions get reset mid-request.
_getaddrinfo = __import__("socket").getaddrinfo
__import__("socket").getaddrinfo = lambda *a, **k: sorted(_getaddrinfo(*a, **k), key=lambda r: r[0] != 2)


def _with_retries(call, what: str, attempts: int = 10):
    last = ""
    for attempt in range(attempts):
        try:
            return call()
        except urllib.error.HTTPError as exc:
            last = f"HTTP {exc.code}: {exc.read()[:200]!r}"
            if exc.code < 500 and exc.code not in (408, 429):
                break
        except UnicodeError as exc:   # a bad header or body is our bug, not the network: retrying can't help
            last = str(exc)
            break
        except Exception as exc:  # noqa: BLE001 — network blips are retryable
            last = str(exc)
        time.sleep(min(8.0, 1.0 * 2 ** attempt))
    raise SystemExit(f"error: {what} failed — {last}")


def clip_path(text: str) -> Path:
    return WORK / "clips" / (hashlib.sha256(f"{MODEL}|{CFG['voice']}|{text}".encode()).hexdigest()[:24] + ".pcm")


def synth(text: str) -> bytes:
    """Kokoro → raw 24 kHz mono s16le PCM (lossless: no MP3 in the middle), cached by text, so a re-run
    only pays for lines that changed. Local mode never gets here for a missing clip: run `voice` first."""
    path = clip_path(text)
    if path.exists():
        return path.read_bytes()
    if CFG["tts"] != "openrouter":
        raise SystemExit(f"error: no clip for {text[:60]!r}; run `voice` first (or set \"tts\": \"openrouter\")")
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise SystemExit("error: set OPENROUTER_API_KEY")
    VOICE = CFG["voice"]
    payload = json.dumps({"model": MODEL, "voice": VOICE, "input": text, "response_format": "pcm"}).encode()

    def call() -> bytes:
        request = urllib.request.Request("https://openrouter.ai/api/v1/audio/speech", data=payload, method="POST",
                                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read()
        if len(data) < SR // 2 or len(data) % 2:
            raise RuntimeError(f"bad PCM ({len(data)} bytes)")
        return data

    data = _with_retries(call, f"TTS for {text[:50]!r}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


_token_lock = __import__("threading").Lock()


def cf_token() -> str:
    """Workers AI auth: CLOUDFLARE_API_TOKEN, else wrangler's OAuth login (refreshed if stale)."""
    if os.environ.get("CLOUDFLARE_API_TOKEN"):
        return os.environ["CLOUDFLARE_API_TOKEN"]
    with _token_lock:
        if getattr(cf_token, "_failed", False):   # one failed login is enough: don't make every worker retry it
            raise SystemExit("error: no Cloudflare token (see above)")
        try:
            return _wrangler_token()
        except SystemExit:
            cf_token._failed = True
            raise


def _wrangler_token() -> str:
    if not WRANGLER_CONFIG.exists():  # newer wrangler keeps its login encrypted: ask it for the token
        cached = getattr(cf_token, "_cached", None)
        if cached and time.time() - cached[1] < 1200:
            return cached[0]
        out = subprocess.run(["npx", "-y", "wrangler@latest", "auth", "token"], capture_output=True, text=True,
                             cwd="/tmp").stdout.splitlines()
        # wrangler prints a banner and a "────" rule around the token: take only a token-shaped line
        found = [line.strip() for line in out if re.fullmatch(r"[A-Za-z0-9._~+/=-]{20,}", line.strip())]
        if not found:
            raise SystemExit("error: no Cloudflare token from wrangler — the login has probably expired. "
                             "Run `npx wrangler login`, or render with --no-verify (or --recheck none)")
        cf_token._cached = (found[-1], time.time())
        return found[-1]

    def read() -> tuple[str, float]:
        conf = WRANGLER_CONFIG.read_text()
        token = re.search(r'oauth_token\s*=\s*"([^"]+)"', conf).group(1)
        expires = re.search(r'expiration_time\s*=\s*"([^"]+)"', conf).group(1)
        stamp = time.mktime(time.strptime(expires[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
        return token, stamp
    token, expires = read()
    if expires - time.time() < 300:
        subprocess.run(["npx", "-y", "wrangler@latest", "whoami"], capture_output=True, check=False)
        token, _ = read()
    return token


def wav_bytes(samples: array.array) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(samples.tobytes())
    return buf.getvalue()


def stt_path(samples: array.array) -> Path:
    return WORK / "stt" / (hashlib.sha256(wav_bytes(samples)).hexdigest()[:24] + ".json")


def whisper(samples: array.array) -> dict:
    """Workers AI whisper-large-v3-turbo → {"text", "words"}. Cached by audio."""
    blob = wav_bytes(samples)
    path = stt_path(samples)
    if path.exists():
        return json.loads(path.read_text())
    body = json.dumps({"audio": base64.b64encode(blob).decode(), "language": "en"}).encode()

    def call() -> dict:
        request = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4/accounts/{cf_account()}/ai/run/@cf/openai/whisper-large-v3-turbo",
            data=body, method="POST",
            headers={"Authorization": f"Bearer {cf_token()}", "Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.load(response)["result"]
        words = [w for seg in result.get("segments", []) for w in seg.get("words", [])]
        return {"text": result.get("text", "").strip(), "words": words}

    out = _with_retries(call, "Whisper")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out))
    return out


def nova(samples: array.array) -> str:
    """Second, independent ear (Deepgram Nova-3 on Workers AI) for lines Whisper doubts."""
    blob = wav_bytes(samples)
    path = WORK / "stt-nova" / (hashlib.sha256(blob).hexdigest()[:24] + ".txt")
    if path.exists():
        return path.read_text()

    def call() -> str:
        request = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4/accounts/{cf_account()}/ai/run/@cf/deepgram/nova-3?smart_format=true",
            data=blob, method="POST", headers={"Authorization": f"Bearer {cf_token()}", "Content-Type": "audio/wav"})
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)["result"]["results"]["channels"][0]["alternatives"][0]["transcript"]

    try:   # a second opinion only: if Nova is slow or down, the line simply stays flagged
        text = _with_retries(call, "Nova-3", attempts=3)
    except SystemExit as exc:
        print(f"note: no Nova second opinion ({exc})", file=sys.stderr)
        return ""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return text


# ---- post-processing ------------------------------------------------------------

WIN = SR // 100            # 10 ms analysis windows
ONSET_DB, OFFSET_DB = -45.0, -50.0
KEEP_LEAD_MS, KEEP_TAIL_MS = 100, 150   # edge silence every clip is normalised to
FADE = SR * 4 // 1000      # 4 ms de-click ramps at the trimmed edges


def as_float(samples) -> "np.ndarray":
    """array.array ('h' or 'f') or raw s16le/f32le bytes → float64 numpy view (no Python loop)."""
    if isinstance(samples, array.array):
        return np.frombuffer(samples, dtype=np.int16 if samples.typecode == "h" else np.float32).astype(np.float64)
    return np.frombuffer(samples, dtype=np.int16).astype(np.float64)


def window_db(samples: array.array) -> list[float]:
    if np is not None:   # 10 ms windows in one pass: a 2-hour file takes seconds, not minutes
        x = as_float(samples)
        full = len(x) // WIN
        energy = (x[: full * WIN].reshape(full, WIN) ** 2).mean(axis=1)
        if len(x) % WIN:
            energy = np.append(energy, (x[full * WIN:] ** 2).mean())
        with np.errstate(divide="ignore"):
            return np.where(energy > 0, 10 * np.log10(energy / 32768.0 ** 2), -120.0).tolist()
    out = []
    for i in range(0, len(samples), WIN):
        w = samples[i:i + WIN]
        energy = sum(x * x for x in w) / max(1, len(w))
        out.append(10 * math.log10(energy / (32768.0 ** 2)) if energy > 0 else -120.0)
    return out


def analyse(samples: array.array, text: str) -> dict:
    db = window_db(samples)
    loud = [i for i, v in enumerate(db) if v > ONSET_DB]
    if not loud:
        return {"silent": True}
    on = loud[0]
    off = max(i for i, v in enumerate(db) if v > OFFSET_DB)
    gap = run = 0
    for v in db[on:off + 1]:
        run = run + 1 if v <= ONSET_DB else 0
        gap = max(gap, run)
    speech_ms = (off + 1 - on) * 10
    speech = samples[on * WIN:(off + 1) * WIN]
    if np is not None:
        s, whole = as_float(speech), np.frombuffer(samples, dtype=np.int16)
        energy = float((s ** 2).mean()) if len(s) else 0.0
        clipped = int(np.count_nonzero((whole == 32767) | (whole == -32768)))
        peak = max(abs(int(whole.min())), int(whole.max()))
    else:
        energy = sum(x * x for x in speech) / max(1, len(speech))
        clipped = sum(1 for x in samples if x in (32767, -32768))
        peak = max(abs(min(samples)), max(samples))
    return {
        "silent": False, "on": on * WIN, "off": min(len(samples), (off + 1) * WIN),
        "lead_ms": on * 10, "tail_ms": (len(db) - 1 - off) * 10, "speech_ms": speech_ms,
        "chars_per_s": round(len(text) / (speech_ms / 1000), 1),
        "max_gap_ms": gap * 10, "rms_db": round(10 * math.log10(max(energy, 1e-12) / 32768.0 ** 2), 1),
        "peak_db": round(20 * math.log10(max(1, peak) / 32768.0), 1),
        "clipped": clipped,
    }


def normalise_edges(samples: array.array, a: dict) -> array.array:
    """Exactly KEEP_LEAD_MS before the first sound and KEEP_TAIL_MS after the last,
    so the silence between lines is the planned pause — never Kokoro's variable padding."""
    lead, tail = SR * KEEP_LEAD_MS // 1000, SR * KEEP_TAIL_MS // 1000
    start, end = max(0, a["on"] - lead), min(len(samples), a["off"] + tail)
    clip = array.array("h", bytes(2 * (lead - (a["on"] - start))))
    clip.extend(samples[start:end])
    clip.extend(array.array("h", bytes(2 * (tail - (end - a["off"])))))
    for i in range(FADE):
        g = i / FADE
        clip[i] = int(clip[i] * g)
        clip[-1 - i] = int(clip[-1 - i] * g)
    return clip


NUMBER_WORDS = {w: str(i) for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen".split())}
SOUNDS_LIKE = {"naught": "0", "eye": "i", "vs": "versus", "be": "b", "bee": "b", "see": "c", "sea": "c", "you": "u",
               "kramers": "cramers", "kramer": "cramer",
               # true homophones: the transcript can't tell them apart, so neither should we
               "colonel": "kernel", "weight": "wait", "gooey": "gui"}


SOUNDS_LIKE.update({"nought": "0", "cue": "q", "queue": "q", "are": "r"})   # letters heard as words, both sides

# Spelled-out numbers become digits on both sides, so "thirty-six" = "36", "one hundred and eighty" = "180"
# and "ten thousand" = "10,000" stop being flagged. "and" only joins after hundred/thousand: "one and two" stays two numbers.
_UNIT = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
         "seventeen eighteen nineteen").split()
_TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()
_U, _T, _N = "|".join(_UNIT[1:10]), "|".join(_TENS), "|".join(sorted(_UNIT, key=len, reverse=True))
_BELOW_100 = rf"(?:(?:{_T})(?:[\s-]+(?:{_U}))?|(?:{_N}))"
_BELOW_1000 = rf"(?:(?:{_U})\s+hundred(?:\s+(?:and\s+)?{_BELOW_100})?|{_BELOW_100})"
SPELLED = re.compile(rf"\b{_BELOW_1000}(?:\s+thousand(?:\s+(?:and\s+)?{_BELOW_1000})?)?\b")


def _spelled(m: re.Match) -> str:
    total = current = 0
    for word in re.split(r"[\s-]+", m.group(0)):
        if word in _UNIT:
            current += _UNIT.index(word)
        elif word in _TENS:
            current += 10 * (_TENS.index(word) + 2)
        elif word == "hundred":
            current *= 100
        elif word == "thousand":
            total, current = (total + current) * 1000, 0
    return str(total + current)


# British and American spellings are the same word to the ear.
SPELLING = [(r"\b(\w*?)meter(s?)\b", r"\1metre\2"), (r"\b(\w*?)liter(s?)\b", r"\1litre\2"),
            (r"\bcenter(s?)\b", r"centre\1"), (r"\b(\w+)yz(e|ed|es|ing)\b", r"\1ys\2"), (r"\b(\w+)iz(e|ed|es|ing)\b", r"\1is\2"),
            (r"\b(colo|behavio|favo|neighbo)r(s?)\b", r"\1ur\2"), (r"\bgray\b", "grey")]

FRACTION = {2: ("half", "halves"), 3: ("third", "thirds"), 4: ("quarter", "quarters"), 5: ("fifth", "fifths")}


def _fraction(m: re.Match) -> str:
    top, bottom = int(m.group(1)), int(m.group(2))
    if bottom in FRACTION:
        return f" {top} {FRACTION[bottom][top != 1]} "
    return f" {top} over {bottom} "


def tokens(text: str) -> list[str]:
    t = text.lower().replace("’", "'").replace("−", "-")
    t = SPELLED.sub(_spelled, t)
    for pattern, replacement in SPELLING:
        t = re.sub(pattern, replacement, t)
    # Math as heard: a transcript may write the symbol for what the voice said in words.
    t = re.sub(r"(\d+)\s*/\s*(\d+)", _fraction, t)               # 2/3 = two thirds
    t = re.sub(r"(?<![\w)])-\s*(?=[\w(])", " minus ", t)          # -2 = minus 2
    t = re.sub(r"(?<=\d)\s*[x×]\s*(?=\d)", " by ", t)             # 2x3 = 2 by 3
    t = re.sub(r"(?<=[a-z])\s*×\s*(?=[a-z])", " cross ", t)       # u × v = u cross v
    t = re.sub(r"\b([a-z])\s*[.·]\s*([a-z])\b", r"\1 dot \2", t)  # u.v = u dot v
    t = t.replace("+", " plus ").replace("=", " equals ").replace("°", " degrees ")
    t = re.sub(r"\bdegree\b", "degrees", t)
    t = re.sub(r"\b(?:twenty twenty|2020)[\s,]+(one|two|three|four|five|six|seven|eight|nine|[1-9])\b",
               lambda m: "202" + NUMBER_WORDS.get(m.group(1), m.group(1)), t)
    t = re.sub(r"(?<=\d),(?=\d)", "", t)
    t = re.sub(r"\b(\d+)\.(\d*?)0+\b", lambda m: m[1] + ("." + m[2] if m[2] else ""), t)   # 0.50 = 0.5
    t = re.sub(r"(?<=\w)-(?=\w)", "", t)        # non-volatile = nonvolatile
    t = re.sub(r"[/\-–—_]", " ", t)
    t = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", t)
    t = re.sub(r"[^\w\s.']", " ", t).replace("'", "")  # retain the spoken s in possessives
    out: list[str] = []
    for word in t.split():
        word = SOUNDS_LIKE.get(NUMBER_WORDS.get(word, word), NUMBER_WORDS.get(word, word))
        letter = len(word) == 1 and (word.isalpha() or word.isdigit())   # "G A O B" = "GAOB"
        if letter and out and out[-1].startswith("\0"):
            out[-1] += word                      # "c p u" and "cpu" compare equal
        elif len(word) == 1 and word.isdigit() and out:
            out[-1] += word                      # "rho 0" = "rho0" (a subscript read aloud)
        else:
            out.append("\0" + word if letter else word)
    return [w.lstrip("\0") for w in out]


def match(expected: list[str], heard: str) -> float:
    """0–1: how closely a transcript matches what the line should say, word by word.
    Strict on purpose — a doubtful line goes to the second recogniser, not a looser metric."""
    heard_forms = [tokens(heard), tokens(heard.replace("-", " "))]   # "R-naught" = "R naught"
    return max(difflib.SequenceMatcher(None, tokens(e), got, autojunk=False).ratio()
               for e in expected for got in heard_forms)


def hear(samples: list[array.array], lines: list[dict], where: str) -> tuple[list[dict], list[str]]:
    """Transcribe every line; a line Whisper doubts gets a second opinion from Nova-3,
    and only fails if neither recogniser hears it."""
    with ThreadPoolExecutor(WORKERS) as pool:
        heard = list(pool.map(whisper, samples))
    results, problems = [], []
    for line, h, audio in zip(lines, heard, samples):
        expected = [line["text"], line["shown"], line["text"].replace("-", " ")]   # "same-potential" = "same potential"
        r = {"heard": h["text"], "match": round(match(expected, h["text"]), 3)}
        if r["match"] < MIN_MATCH:
            r["nova"] = nova(audio)
            r["nova_match"] = round(match(expected, r["nova"]), 3)
            if r["nova_match"] < MIN_MATCH:
                problems.append(f"{where} line {line['i']}: said {line['text']!r} → Whisper {h['text']!r}, "
                                f"Nova {r['nova']!r}")
        results.append(r)
    return results, problems


def ebur128(path: Path, peak: bool = True) -> dict:
    """Integrated loudness, and the true peak when asked (4x oversampling: six times slower)."""
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                           "ebur128=peak=true" if peak else "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    summary = proc.stderr.rsplit("Summary:", 1)[-1]
    lufs = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summary).group(1))
    if not peak:
        return {"lufs": lufs}
    return {"lufs": lufs, "true_peak_db": float(re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", summary).group(1))}


def ffmpeg(*args: str) -> None:
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], capture_output=True)
    if proc.returncode:
        raise SystemExit(f"error: ffmpeg — {proc.stderr.decode()[:300]}")


# Spoken-word mono target (= -16 LUFS stereo). Kokoro peaks ~18 dB above its RMS, so a
# lookahead limiter catches the rare plosive peaks (<1% of speech) instead of the whole
# file staying quiet; nothing else touches the voice.
TARGET_LUFS, PEAK_CEILING_DB, LIMITER_DB = -19.0, -1.0, -2.0
MP3_BITRATE = "96k"   # CBR: browsers seek CBR exactly, so a clicked line starts on its word
MIN_MATCH = 0.85


def limiter_windows(plain: bytes, limited: bytes) -> tuple[int, int]:
    """(voiced 10 ms windows, windows the limiter pulled down by more than 0.5 dB), from f32le audio."""
    if np is not None:
        a, b = np.abs(np.frombuffer(plain, dtype=np.float32)), np.abs(np.frombuffer(limited, dtype=np.float32))
        n = len(range(0, min(len(a), len(b)) - WIN, WIN))
        pa, la = a[: n * WIN].reshape(n, WIN).max(axis=1), b[: n * WIN].reshape(n, WIN).max(axis=1)
        voiced = pa >= 0.02
        return int(voiced.sum()), int((20 * np.log10(pa[voiced] / np.maximum(1e-9, la[voiced])) > 0.5).sum())
    a, b = array.array("f", plain), array.array("f", limited)
    voiced = touched = 0
    for i in range(0, min(len(a), len(b)) - WIN, WIN):
        peak = max(abs(x) for x in a[i:i + WIN])
        if peak < 0.02:
            continue
        voiced += 1
        touched += 20 * math.log10(peak / max(1e-9, max(abs(x) for x in b[i:i + WIN]))) > 0.5
    return voiced, touched


def previous_mp3_results() -> dict:
    """Clip name → the transcript of that clip heard out of the last rendered MP3 (empty on a first render)."""
    try:
        detail = json.loads((WORK / "report.json").read_text()).get("detail", [])
    except (OSError, ValueError):
        return {}
    return {clip_path(d["text"]).name: d["mp3"] for d in detail
            if isinstance(d.get("mp3"), dict) and d["mp3"].get("heard") is not None}


def rescore(r: dict, line: dict, where: str) -> tuple[dict, str | None]:
    """A transcript kept from an earlier run, scored again with today's matcher (no network)."""
    expected = [line["text"], line["shown"], line["text"].replace("-", " ")]
    r = {**r, "match": round(match(expected, r["heard"]), 3), "carried": True}
    if "nova" in r:
        r["nova_match"] = round(match(expected, r["nova"]), 3)
    if r["match"] < MIN_MATCH and r.get("nova_match", 0) < MIN_MATCH:
        return r, f"{where} line {line['i']}: said {line['text']!r} → Whisper {r['heard']!r}, Nova {r.get('nova', '')!r}"
    return r, None


def pick_lines(spec: str, lines: list[dict]) -> list[dict]:
    """"40-60,75" (line numbers as report.json and status print them) or any text the lines contain."""
    if re.fullmatch(r"[\d\s,-]+", spec):
        wanted = set()
        for part in filter(None, (p.strip() for p in spec.split(","))):
            a, _, b = part.partition("-")
            wanted.update(range(int(a), int(b or a) + 1))
        return [line for line in lines if line["i"] in wanted]
    needle = spec.lower()
    return [line for line in lines if needle in line["text"].lower() or needle in line["shown"].lower()]


def render_preview(spec: str, lines: list[dict], trimmed: list[array.array], comp_ms: int) -> int:
    """Only the chosen lines, with their planned pauses and the same loudness target → preview.mp3.
    No checks, and the full MP3, timeline and report stay as they were: this is for listening to a fix."""
    chosen = pick_lines(spec, lines)
    if not chosen:
        raise SystemExit(f"error: --preview {spec!r} matches no line")
    program = array.array("h")
    for line in chosen:
        program.extend(trimmed[line["i"]])
        program.extend(array.array("h", bytes(2 * (SR * (line["pause"] + comp_ms) // 1000))))
    wav, mp3 = WORK / "preview.wav", WORK / "preview.mp3"
    wav.write_bytes(wav_bytes(program))
    lufs = ebur128(wav)["lufs"]
    gain = round(TARGET_LUFS - lufs, 2) if lufs > -60 else 0.0   # under ~3 s, ebur128 has no reading
    limit = 10 ** (LIMITER_DB / 20)
    ffmpeg("-i", str(wav), "-af", f"volume={gain}dB,alimiter=limit={limit:.4f}:attack=5:release=60:level=0",
           "-ar", str(SR), "-ac", "1", "-c:a", "libmp3lame", "-b:a", MP3_BITRATE, str(mp3))
    wav.unlink()
    for line in chosen:
        print(f"  {line['i']:>5}  {line['text']}")
    print(f"preview: {len(chosen)} line(s), {len(program) * 1000 // SR / 1000:.1f} s → {mp3}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    started = time.time()
    blocks, lines = plan_lines()
    errors = check_lines(lines)
    if errors:
        for e in errors:
            print("error:", e, file=sys.stderr)
        return 1
    WORK.mkdir(parents=True, exist_ok=True)

    # 1) Voice every line (cached, concurrent).
    print(f"synthesising {len(lines)} lines with {MODEL} ({CFG['voice']}, {CFG['tts']})...", flush=True)
    with ThreadPoolExecutor(WORKERS) as pool:
        raw = list(pool.map(lambda line: synth(line["text"]), lines))
    clips = [array.array("h", r) for r in raw]

    # 2) Measure every clip; normalise its edges.
    stats = [analyse(c, line["text"]) for c, line in zip(clips, lines)]
    problems: list[str] = []
    for line, st in zip(lines, stats):
        if st["silent"]:
            problems.append(f"line {line['i']} is silent: {line['text']!r}")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    rms = sorted(st["rms_db"] for st in stats)
    median_rms = rms[len(rms) // 2]
    for line, st in zip(lines, stats):
        why = []
        if st["clipped"]:
            why.append(f"{st['clipped']} clipped samples")
        if st["max_gap_ms"] > 900:
            why.append(f"{st['max_gap_ms']} ms gap inside the line")
        if len(line["text"]) >= 25 and not 9 <= st["chars_per_s"] <= 24:
            why.append(f"{st['chars_per_s']} chars/s")
        if abs(st["rms_db"] - median_rms) > 5:
            why.append(f"level {st['rms_db']} dB vs median {median_rms}")
        if why:
            problems.append(f"line {line['i']} ({', '.join(why)}): {line['text']!r}")
    leads = sorted(st["lead_ms"] for st in stats)
    tails = sorted(st["tail_ms"] for st in stats)
    natural = leads[len(leads) // 2] + tails[len(tails) // 2]
    # Flooki's pauses sit on top of Kokoro's natural edge silence; keep that feel exactly.
    comp_ms = natural - KEEP_LEAD_MS - KEEP_TAIL_MS
    trimmed = [normalise_edges(c, st) for c, st in zip(clips, stats)]
    if args.preview:
        return render_preview(args.preview, lines, trimmed, comp_ms)

    # 3) Ear check: Whisper must hear what each line should say. Transcripts are cached by audio,
    #    so only new clips go over the network; every line is scored again with today's matcher.
    verify = verifying() and not args.no_verify
    recheck = (args.recheck or CFG["recheck"]) if verify else "none"
    if verify and (recheck != "none" or any(not stt_path(c).exists() for c in trimmed)):
        cf_account(), cf_token()   # an expired login fails here, in seconds, not after encoding the whole MP3
    if verify:
        print("verifying every clip with Whisper (Nova-3 second opinion)...", flush=True)
        heard, issues = hear(trimmed, lines, "clip")
        problems += issues
    else:
        print("not verifying (verify: none or --no-verify)", flush=True)
        heard = [{"heard": None, "match": None} for _ in lines]

    # 4) Stitch: clip, then its exact pause. Timeline in ms, sample-accurate.
    program = array.array("h")
    timeline = []
    for line, clip in zip(lines, trimmed):
        t0 = len(program)
        program.extend(clip)
        t1 = len(program)
        program.extend(array.array("h", bytes(2 * (SR * (line["pause"] + comp_ms) // 1000))))
        timeline.append({"i": line["i"], "b": line["b"], "s": line["s"], "e": line["e"],
                         "t0": round(t0 * 1000 / SR), "t1": round(t1 * 1000 / SR), "section": line["section"]})
    total_ms = round(len(program) * 1000 / SR)
    assembled = WORK / "assembled.wav"
    assembled.write_bytes(wav_bytes(program))

    # 5) Loudness: one gain to the target, a transparent peak limiter, then a trim so the
    #    encoded MP3's true peak stays under the ceiling.
    print(f"mastering and encoding {total_ms // 60000} min of audio ({time.time() - started:.0f}s so far)...", flush=True)
    before = ebur128(assembled, peak=False)
    gain = round(TARGET_LUFS - before["lufs"], 2)
    limit = 10 ** (LIMITER_DB / 20)
    chain = f"volume={gain}dB,alimiter=limit={limit:.4f}:attack=5:release=60:level=0:latency=1"
    mastered = WORK / "mastered.wav"
    ffmpeg("-i", str(assembled), "-af", chain, "-ar", str(SR), "-ac", "1", "-c:a", "pcm_f32le", str(mastered))
    mp3 = WORK / "notes.mp3"
    trim = 0.0
    for _ in range(4):
        ffmpeg("-i", str(mastered), "-af", f"volume={trim}dB", "-ar", str(SR), "-ac", "1",
               "-c:a", "libmp3lame", "-b:a", MP3_BITRATE, "-compression_level", str(CFG["mp3_quality"]),
               "-id3v2_version", "3", "-metadata", f"title={page_title()}",
               "-metadata", f"album={CFG['album']}", "-metadata", f"artist={CFG['artist']}", str(mp3))
        after = ebur128(mp3)
        if after["true_peak_db"] <= PEAK_CEILING_DB:
            break
        trim = round(trim + PEAK_CEILING_DB - after["true_peak_db"] - 0.1, 2)
    else:
        problems.append(f"true peak {after['true_peak_db']} dBTP is over {PEAK_CEILING_DB}")
    plain = subprocess.run(["ffmpeg", "-v", "error", "-i", str(assembled), "-af", f"volume={gain}dB",
                            "-f", "f32le", "-"], capture_output=True).stdout
    limited = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mastered), "-f", "f32le", "-"],
                             capture_output=True).stdout
    voiced, touched = limiter_windows(plain, limited)
    del plain, limited
    limiter_share = round(touched / max(1, voiced), 4)
    if limiter_share > 0.03:
        problems.append(f"the limiter is working on {limiter_share:.1%} of speech — lower TARGET_LUFS")

    # 6) Verify the finished MP3 itself: duration, alignment, and every line re-heard
    #    from its own timeline slot.
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=bit_rate,sample_rate",
                            "-of", "json", str(mp3)], capture_output=True, text=True)
    info = json.loads(probe.stdout)
    mp3_ms = round(float(info["format"]["duration"]) * 1000)
    decoded = array.array("h", subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "s16le", "-ac", "1",
                                               "-ar", str(SR), "-"], capture_output=True).stdout)
    a_env, b_env = window_db(program[: SR * 90]), window_db(decoded[: SR * 90])
    def corr(lag: int) -> float:
        pairs = zip(a_env[max(0, -lag):], b_env[max(0, lag):])
        return sum((x > -60) == (y > -60) for x, y in pairs)
    offset_ms = 10 * max(range(-10, 11), key=corr)
    if abs(mp3_ms - total_ms) > 120:
        problems.append(f"MP3 is {mp3_ms} ms but the timeline is {total_ms} ms")
    if abs(offset_ms) > 30:
        problems.append(f"MP3 is offset {offset_ms} ms from the timeline")

    # Re-hearing every line out of a 2-hour MP3 is most of a render, and a re-encode changes every
    # byte, so nothing is cached. By default only lines whose clip is new or changed are re-heard,
    # plus evenly spaced spot checks that would catch any timing drift; the rest keep their
    # transcript from the last render (scored again with today's matcher).
    if recheck != "none":
        old = previous_mp3_results() if recheck == "changed" else {}
        fresh = [n for n, line in enumerate(lines) if clip_path(line["text"]).name not in old]
        rest = [n for n in range(len(lines)) if clip_path(lines[n]["text"]).name in old]
        spot = CFG["spot_checks"] if args.spot is None else args.spot
        spots = {rest[round(k * (len(rest) - 1) / max(1, spot - 1))] for k in range(min(spot, len(rest)))}
        todo = sorted(set(fresh) | spots)
        print(f"re-hearing {len(todo)} of {len(lines)} lines out of the finished MP3 "
              f"({len(fresh)} new or changed, {len(todo) - len(fresh)} spot checks)...", flush=True)
        slices = [decoded[SR * timeline[n]["t0"] // 1000: SR * timeline[n]["t1"] // 1000] for n in todo]
        results, mp3_issues = hear(slices, [lines[n] for n in todo], "MP3")
        reheard = [None] * len(lines)
        for n, r in zip(todo, results):
            reheard[n] = r
        for n, line in enumerate(lines):
            if reheard[n] is None:
                reheard[n], issue = rescore(old[clip_path(line["text"]).name], line, "MP3")
                if issue:
                    mp3_issues.append(issue)
        problems += sorted(mp3_issues, key=lambda p: int(re.search(r"line (\d+)", p).group(1)))
    else:   # nothing re-heard now: unchanged lines keep the last render's MP3 transcript, changed ones have none yet
        old = previous_mp3_results() if verify else {}
        reheard = [rescore(old[clip_path(line["text"]).name], line, "MP3")[0]
                   if clip_path(line["text"]).name in old else {"heard": None, "match": None} for line in lines]

    def mean(results: list[dict]) -> float | None:
        got = [r["match"] for r in results if r.get("match") is not None]
        return round(sum(got) / len(got), 3) if got else None

    gaps = sorted(set(line["pause"] + comp_ms + KEEP_LEAD_MS + KEEP_TAIL_MS for line in lines))
    words = sum(len(line["text"].split()) for line in lines)
    speech_ms = sum(t["t1"] - t["t0"] for t in timeline)
    report = {
        "voice": f"{MODEL} / {CFG['voice']} ({CFG['tts']})", "verified": verify, "lines": len(lines), "words": words,
        "duration": f"{total_ms // 60000}:{total_ms // 1000 % 60:02d}", "duration_ms": total_ms, "mp3_ms": mp3_ms,
        "mp3_bytes": mp3.stat().st_size, "bitrate": MP3_BITRATE, "words_per_minute": round(words / (speech_ms / 60000)),
        "silence_share": round(1 - speech_ms / total_ms, 3),
        "kokoro_natural_edges_ms": natural, "edge_compensation_ms": comp_ms,
        "effective_gaps_ms": gaps, "loudness_before": before, "gain_db": gain, "trim_db": trim,
        "limiter_touched_share": limiter_share, "loudness_after": after,
        "mp3_offset_ms": offset_ms,
        "clip_match": {"whisper_mean": mean(heard),
                       "second_opinions": sum("nova" in r for r in heard)},
        "mp3_match": {"whisper_mean": mean(reheard),
                      "second_opinions": sum("nova" in r for r in reheard),
                      "reheard": sum(not r.get("carried") for r in reheard) if recheck != "none" else 0,
                      "kept_from_last_render": sum(bool(r.get("carried")) for r in reheard)},
        "render_seconds": round(time.time() - started),
        "problems": problems,
    }
    detail = [{"i": line["i"], "text": line["text"], "clip": h, "mp3": rh,
               **{k: v for k, v in st.items() if k not in ("on", "off", "silent")}}
              for line, h, rh, st in zip(lines, heard, reheard, stats)]
    (WORK / "timeline.json").write_text(json.dumps({"duration": total_ms, "lines": timeline}))
    (WORK / "report.json").write_text(json.dumps({**report, "detail": detail}, indent=1, ensure_ascii=False))
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


# ---- local voice (Kokoro on this machine) -------------------------------------

# Kokoro (misaki) reads a lone capital "A" as the article "uh". In math and notes, A is usually a matrix
# or a variable, so it gets the letter's phonemes, except where it starts a sentence and is followed by
# an ordinary word or a number ("A matrix is...", "A 2 by 2 inverse..."): that A is the article.
LETTER_A = "[A](/ˈA/)"
NOT_A_NOUN = {"is", "inverse", "transpose", "times", "equals", "equal", "has", "and", "plus", "minus", "squared",
              "with", "by", "to", "cross", "dot", "of"}


def pronounce(text: str) -> str:
    if not CFG["letter_a"]:
        return text

    def one(m: re.Match) -> str:
        before = text[:m.start()].rstrip()
        starts = not before or before[-1] in ".:;?!"
        nxt = re.match(r"\s*([A-Za-z0-9]+)", text[m.end():])
        word = nxt.group(1) if nxt else ""
        article = starts and (word[:1].isdigit() or (len(word) > 1 and word[0].islower() and word not in NOT_A_NOUN))
        return "A" if article else LETTER_A
    return re.sub(r"\bA\b", one, text)


def cmd_voice(args: argparse.Namespace) -> int:
    """Voice the planned lines with Kokoro on this machine, into the same cache `render` reads."""
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    # Once the weights are cached, never ask Hugging Face again: a flaky network otherwise stalls every run.
    if (Path.home() / ".cache" / "huggingface" / "hub" / "models--hexgrad--Kokoro-82M").exists():
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
    try:
        import numpy as np
        from kokoro import KPipeline
    except ImportError:
        raise SystemExit("error: Kokoro is not installed here; run tools/setup.sh and use its venv's python")
    plan_file = WORK / "plan.json"
    if not plan_file.exists():
        raise SystemExit("error: run `plan` first")
    lines = json.loads(plan_file.read_text())["lines"]
    pipe = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")

    def voice(text: str) -> tuple[bytes, str]:
        parts, phonemes = [], []
        for result in pipe(pronounce(text), voice=CFG["voice"], speed=1.0, split_pattern=None):
            audio = result.audio.cpu().numpy() if hasattr(result.audio, "cpu") else np.asarray(result.audio)
            parts.append(audio)
            phonemes.append(result.phonemes)
        wave_ = np.concatenate(parts) if parts else np.zeros(SR // 2, dtype=np.float32)
        return (np.clip(wave_, -1.0, 1.0) * 32767.0).round().astype("<i2").tobytes(), " | ".join(phonemes)

    if args.say:
        pcm, phonemes = voice(args.say)
        print(pronounce(args.say))
        print(phonemes)
        print(f"{len(pcm) // 2 * 1000 // SR} ms")
        return 0
    todo = list(dict.fromkeys(line["text"] for line in lines if args.all or not clip_path(line["text"]).exists()))
    print(f"voicing {len(todo)} of {len(lines)} lines locally ({CFG['voice']})", flush=True)
    start = time.time()
    for n, text in enumerate(todo, 1):
        pcm, _ = voice(text)
        path = clip_path(text)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(pcm)
        tmp.replace(path)
        if n % 25 == 0 or n == len(todo):
            print(f"  {n}/{len(todo)}  {time.time() - start:.0f}s", flush=True)
    return 0


# ---- publish --------------------------------------------------------------------


def page_title() -> str:
    if CFG["title"]:
        return CFG["title"]
    soup = BeautifulSoup(original_html(), "html.parser")
    h1 = soup.select_one(f'{CFG["root"]} h1[data-say]') or soup.select_one("h1[data-say]")
    if h1 is not None:
        return re.sub(r"\.$", "", h1["data-say"]).replace(". ", " · ", 1)
    return soup.title.get_text().strip() if soup.title else SLUG


def _head(url: str, extra: dict | None = None) -> tuple[int, dict]:
    def call() -> tuple[int, dict]:
        request = urllib.request.Request(url, method="GET" if extra else "HEAD",
                                         headers={"User-Agent": "Mozilla/5.0 (read-along check)", **(extra or {})})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status, dict(response.headers)
        except urllib.error.HTTPError as exc:
            return exc.code, dict(exc.headers)
    return _with_retries(call, f"GET {url}")


def put_audio(mp3: Path) -> str:
    """Upload or place the MP3; returns the URL the page uses. Content-addressed: a new render is a new name."""
    digest = hashlib.sha256(mp3.read_bytes()).hexdigest()[:16]
    pub = CFG["publish"]
    if pub.get("mode", "local") == "local":
        folder = PAGE.parent / pub.get("folder", "audio")
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob(f"{SLUG}-*.mp3"):
            if old.name != f"{SLUG}-{digest}.mp3":
                old.unlink()
        target = folder / f"{SLUG}-{digest}.mp3"
        shutil.copyfile(mp3, target)
        print(f"placed {target.relative_to(PAGE.parent)} ({mp3.stat().st_size // 1024} KB)")
        return os.path.relpath(target, PAGE.parent).replace(os.sep, "/")
    if pub["mode"] != "r2":
        raise SystemExit(f"error: unknown publish mode {pub['mode']!r}")
    key = f"{pub.get('prefix', '').strip('/') + '/' if pub.get('prefix') else ''}{SLUG}-{digest}.mp3"
    url = f"{pub['public_url'].rstrip('/')}/{key}"
    # Probe with a throwaway query: asking for the real URL before it exists makes the edge cache that 404.
    status, headers = _head(f"{url}?probe={time.time_ns()}")
    if status != 200:
        print(f"uploading {mp3.stat().st_size // 1024} KB → r2://{pub['bucket']}/{key}", flush=True)
        subprocess.run(["npx", "-y", "wrangler@latest", "r2", "object", "put", f"{pub['bucket']}/{key}", "--file", str(mp3),
                        "--content-type", "audio/mpeg", "--cache-control", "public, max-age=31536000, immutable",
                        "--remote"], check=True, capture_output=True, cwd=str(WORK))   # cwd: keep .wrangler/ out of the repo
        status, headers = _head(url)
    ranged, _ = _head(url, {"Range": "bytes=0-1023"})
    size = int(headers.get("Content-Length", "0"))
    if status != 200 or size != mp3.stat().st_size or ranged != 206:
        raise SystemExit(f"error: {url} → HTTP {status}, {size} bytes, range {ranged}")
    print(f"live: {url} ({size} bytes, range requests OK)")
    return url


def player_assets() -> str:
    """Where the page loads read-along.js/.css from (relative), copying the skill's player if asked."""
    if CFG["player"] == "copy":
        folder = PAGE.parent / "read-along"
        folder.mkdir(exist_ok=True)
        for name in ("read-along.js", "read-along.css"):
            shutil.copyfile(SKILL / "assets" / name, folder / name)
    else:
        folder = (PAGE.parent / CFG["player"]).resolve() if not Path(CFG["player"]).is_absolute() else Path(CFG["player"])
    if not (folder / "read-along.js").exists():
        raise SystemExit(f"error: no read-along.js in {folder}")
    return folder


def cmd_publish(args: argparse.Namespace) -> int:
    report = json.loads((WORK / "report.json").read_text())
    if report["problems"] and not args.force:
        print("refusing: the render has open problems (see report.json); fix them, or pass --force when "
              "every one is a known false alarm (homophones, letters heard as words)", file=sys.stderr)
        for p in report["problems"]:
            print("  ", p, file=sys.stderr)
        return 1
    timeline = json.loads((WORK / "timeline.json").read_text())
    blocks, lines = plan_lines()
    if [line["text"] for line in lines] != [line["text"] for line in report["detail"]]:
        print("refusing: narration changed since the render — run render again", file=sys.stderr)
        return 1
    if [(line["b"], line["s"], line["e"]) for line in lines] != [(t["b"], t["s"], t["e"]) for t in timeline["lines"]]:
        print("refusing: the page changed since the render — run render again", file=sys.stderr)
        return 1

    url = put_audio(WORK / "notes.mp3")
    soup = BeautifulSoup(original_html(), "html.parser")
    sections = []
    for line in lines:
        if line["role"] == "heading":
            sections.append({"n": line["section"], "t": timeline["lines"][line["i"]]["t0"],
                             "label": re.sub(r"\s+", " ", line["shown"]).strip()})
    data = {
        "id": SLUG, "audio": url, "duration": timeline["duration"], "root": CFG["root"], "selector": CFG["selector"],
        "title": soup.title.get_text().strip() if soup.title else page_title(), "artist": CFG["artist"],
        "album": CFG["album"], "leaf": CFG["leaf"],
        "blockLengths": [b["len"] for b in blocks], "sections": sections,
        "lines": [[t["b"], t["s"], t["e"], t["t0"], t["t1"], t["section"]] for t in timeline["lines"]],
    }
    assets = player_assets()
    rel = os.path.relpath(assets, PAGE.parent).replace(os.sep, "/")
    version = hashlib.sha256((assets / "read-along.js").read_bytes() + (assets / "read-along.css").read_bytes()).hexdigest()[:8]
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    theme = ('<script>try{if(localStorage.getItem("y3f-theme")==="dark")'
             'document.documentElement.classList.add("ra-dark")}catch(e){}</script>')  # dark mode before first paint
    head_block = f'{START}{theme}<link rel="stylesheet" href="{rel}/read-along.css?v={version}">{END}\n'
    body_block = (f'{START}<script type="application/json" id="read-along-data">{payload}</script>'
                  f'<script src="{rel}/read-along.js?v={version}" defer></script>{END}')
    original = original_html()
    if "</head>" not in original or "</body>" not in original:
        raise SystemExit("error: the page needs a </head> and a </body>")
    page = original.replace("</head>", head_block + "</head>", 1).replace("</body>", body_block + "</body>", 1)
    PAGE.write_text(page, encoding="utf-8")
    if original_html() != original:
        print("error: injection is not reversible — the page would have changed", file=sys.stderr)
        return 1
    print(f"wrote {PAGE} ({len(data['lines'])} lines, {len(sections)} chapters; page content unchanged)")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    """What changed since the last render, and what voice / render / publish still have to do. Changes nothing."""
    blocks, lines = plan_lines()
    texts = [line["text"] for line in lines]
    errors = check_lines(lines)
    print(f"page: {len(blocks)} blocks, {len(lines)} lines"
          + (f", {len(errors)} with symbols the voice can't say → fix, then plan" if errors else ""))
    unvoiced = list(dict.fromkeys(t for t in texts if not clip_path(t).exists()))
    print(f"voice: {len(unvoiced)} line(s) without a clip" + (" → run voice" if unvoiced else ""))
    try:
        report = json.loads((WORK / "report.json").read_text())
        timeline = json.loads((WORK / "timeline.json").read_text())
    except (OSError, ValueError):
        print("render: never rendered → run render")
        return 0
    old = [d["text"] for d in report["detail"]]
    if old == texts:
        moved = [(l["b"], l["s"], l["e"]) for l in lines] != [(t["b"], t["s"], t["e"]) for t in timeline["lines"]]
        print("render: same narration, but the page moved its lines → run render" if moved else
              f"render: up to date, {report['duration']}, {len(report['problems'])} flagged line(s) in report.json")
    else:
        ops = difflib.SequenceMatcher(None, old, texts, autojunk=False).get_opcodes()
        new = [j for tag, _, _, j1, j2 in ops if tag in ("replace", "insert") for j in range(j1, j2)]
        gone = sum(i2 - i1 for tag, i1, i2, _, _ in ops if tag in ("replace", "delete"))
        print(f"render: stale — {len(new)} new or changed line(s), {gone} removed → run render "
              f"(re-hears those plus {CFG['spot_checks']} spot checks)")
        for j in new[:25]:
            print(f"  + {j:>5}  {texts[j][:110]}")
        if len(new) > 25:
            print(f"  … and {len(new) - 25} more")
    found = re.search(r'<script type="application/json" id="read-along-data">(.*?)</script>',
                      PAGE.read_text(encoding="utf-8"), re.S)
    if not found:
        print("publish: the page has no player → run publish")
        return 0
    audio = json.loads(found.group(1))["audio"]
    mp3 = WORK / "notes.mp3"
    digest = hashlib.sha256(mp3.read_bytes()).hexdigest()[:16] if mp3.exists() else "?"
    print(f"publish: the page plays {audio}" + ("" if digest in audio else " → not the last render; run publish"))
    return 0


def cmd_strip(_: argparse.Namespace) -> int:
    """Remove the player from the page again (the page content is untouched)."""
    PAGE.write_text(original_html(), encoding="utf-8")
    print(f"removed the read-along blocks from {PAGE}")
    return 0


def load_env(path: str) -> None:
    """OPENROUTER_API_KEY from a KEY=value file (also accepts open_router_key). Never printed."""
    for line in Path(path).expanduser().read_text().splitlines():
        name, _, value = line.partition("=")
        if name.strip().lower().replace("_", "") in ("openrouterapikey", "openrouterkey") and value.strip():
            os.environ.setdefault("OPENROUTER_API_KEY", value.strip().strip("'\""))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", help="readalong.json")
    parser.add_argument("--env-file", help="file holding the OpenRouter key (tts: openrouter)")
    sub_ = parser.add_subparsers(dest="cmd", required=True)
    sub_.add_parser("plan")
    sub_.add_parser("status", help="what changed since the last render; what voice/render/publish still need")
    voice = sub_.add_parser("voice")
    voice.add_argument("--all", action="store_true", help="re-voice lines that already have a clip")
    voice.add_argument("--say", help="print how one sentence is phonemised and its length; write nothing")
    render = sub_.add_parser("render")
    render.add_argument("--recheck", choices=("changed", "all", "none"),
                        help="lines re-heard out of the finished MP3: new/changed + spot checks (default), all, none")
    render.add_argument("--spot", type=int, help="spot checks among unchanged lines (default: config spot_checks, 12)")
    render.add_argument("--no-verify", action="store_true", help="skip Whisper/Nova entirely: a quick draft render")
    render.add_argument("--preview", metavar="LINES",
                        help='only these lines → preview.mp3 to listen to ("40-60,75" or text they contain)')
    publish = sub_.add_parser("publish")
    publish.add_argument("--force", action="store_true", help="publish although the report lists problems")
    sub_.add_parser("strip")
    args = parser.parse_args()
    load_config(args.config)
    if args.env_file:
        load_env(args.env_file)
    return {"plan": cmd_plan, "status": cmd_status, "voice": cmd_voice, "render": cmd_render,
            "publish": cmd_publish, "strip": cmd_strip}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
