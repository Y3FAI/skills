#!/usr/bin/env python3
"""Check, review and publish Flooki exams (https://flooki.app). Python 3.8+, standard library only.

    python3 flooki.py check   EXAM.json [...]            validate against the Flooki API rules
    python3 flooki.py show    EXAM.json                  print the exam as a student would read it
    python3 flooki.py shuffle EXAM.json [--seed TEXT]    shuffle multiple-choice options (in place)
    python3 flooki.py payload EXAM.json                  print the exact request body (no token)
    python3 flooki.py publish EXAM.json [...] [--dry-run] [--again]

EXAM.json is the API request body with `questions` as a plain array (a JSON string is accepted too):
{"title", "description", "metadata": {...}, "questions": [...]}. Extra fields on a question (for example
"source") are kept in the file for your records and stripped before sending. `publish` writes the
exam link back into the file under "published", and skips files whose content is already published.

The token is read from $FLOOKI_SERVICE_TOKEN, else from --env-file (a .env that defines it), else from
~/.config/flooki/token (or --token-file). It is never printed.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

API = "https://flooki.app/api/agent/create-exam"
TRIES = 6   # flooki.app sometimes resets connections
TOKEN_FILE = Path.home() / ".config" / "flooki" / "token"
TYPES = {"multiple_choice", "true_false", "short_answer"}
EXAM_TYPES = {"quiz", "midterm", "final", "other"}
SENT = ("type", "topic", "text", "img", "options", "correctIndex", "correctAnswer", "explanation")
MERMAID = re.compile(r"^\s*(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram(-v2)?|erDiagram|gantt|pie|"
                     r"gitGraph|mindmap|timeline|journey|quadrantChart|xychart-beta|block-beta)\b")
# Flooki's rule: a question must stand on its own, with no pointers to where it came from.
SOURCE_TALK = re.compile(r"\b(slides?|lectures?|class notes|question bank|the bank|past (paper|exam)s?|pdf|"
                         r"textbook|the (paper|set)'?s?)\b|\[cite", re.I)
KEEP_LAST = re.compile(r"\b(all|none|both) (of )?(the )?(above|these)\b|^\s*(both|neither)\b", re.I)
ERRORS = {
    "UNAUTHORIZED": "the token is missing or wrong",
    "MISSING_REQUIRED_FIELDS": "title missing, or questions is not a JSON string",
    "INVALID_TITLE": "the title is empty or not a string",
    "QUESTIONS_TOO_LONG": "the questions string is over 200,000 characters: split the exam",
    "INVALID_METADATA": "description or metadata is invalid (check examType / customExamType)",
    "INVALID_QUESTION_STRUCTURE": "a question does not match Flooki's schema",
    "NO_VALID_QUESTIONS": "the questions array is empty",
    "TOO_MANY_QUESTIONS": "more than 500 questions",
    "SERVER_ERROR": "Flooki failed on its side: try again later",
}


# ------------------------------------------------------------------ files

def load(path: Path) -> dict:
    exam = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(exam, list):
        raise SystemExit(f"{path}: the root is an array. Wrap it: {{\"title\": ..., \"questions\": [...]}}")
    if isinstance(exam.get("questions"), str):
        exam["questions"] = json.loads(exam["questions"])
    return exam


def save(path: Path, exam: dict) -> None:
    path.write_text(json.dumps(exam, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean(q: dict) -> dict:
    return {k: q[k] for k in SENT if k in q}


def body(exam: dict) -> dict:
    out = {"title": exam["title"]}
    for k in ("description", "metadata"):
        if exam.get(k):
            out[k] = exam[k]
    out["questions"] = json.dumps([clean(q) for q in exam["questions"]], ensure_ascii=False)
    return out


def digest(b: dict) -> str:
    return hashlib.sha256(json.dumps(b, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


# ------------------------------------------------------------------ check

def _text(s) -> bool:
    return isinstance(s, str) and s.strip() != ""


def _dollars_balanced(s: str) -> bool:
    return len(re.findall(r"(?<!\\)\$", s)) % 2 == 0


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\\[a-z]+", "", s.lower()))


def check(exam: dict) -> tuple[list[str], list[str]]:
    """(errors, warnings). Errors are what the API rejects; warnings are what makes a weaker exam."""
    err, warn = [], []
    if not _text(exam.get("title")):
        err.append("title: required")
    elif len(exam["title"]) > 200:
        err.append("title: over 200 characters")
    if "description" in exam and (not isinstance(exam["description"], str) or len(exam["description"]) > 500):
        err.append("description: must be a string of at most 500 characters")
    meta = exam.get("metadata") or {}
    for k, n in (("subject", 100), ("institution", 100), ("customExamType", 50)):
        if k in meta and (not _text(meta[k]) or len(meta[k]) > n):
            err.append(f"metadata.{k}: must be a non-empty string of at most {n} characters")
    et = meta.get("examType")
    if et is not None and et not in EXAM_TYPES:
        err.append(f"metadata.examType: {et!r} is not one of {sorted(EXAM_TYPES)}")
    if et == "other" and not meta.get("customExamType"):
        err.append("metadata.customExamType: required when examType is \"other\"")
    if et != "other" and "customExamType" in meta:
        err.append("metadata.customExamType: only allowed when examType is \"other\"")
    for k in ("points", "isPublished"):
        if k in exam:
            err.append(f"{k}: not part of the API")

    qs = exam.get("questions")
    if not isinstance(qs, list) or not qs:
        return err + ["questions: need an array of 1 to 500 questions"], warn
    if len(qs) > 500:
        err.append(f"questions: {len(qs)} is over the 500 limit")
    if len(body(exam)["questions"]) > 200_000:
        err.append("questions: the JSON string is over 200,000 characters; split the exam")

    seen: list[tuple[str, int]] = []
    for i, q in enumerate(qs, 1):
        at = f"Q{i}"
        t = q.get("type")
        if t not in TYPES:
            err.append(f"{at}: type {t!r} is not one of {sorted(TYPES)}")
            continue
        for k in ("text", "explanation"):
            if not _text(q.get(k)):
                err.append(f"{at}: {k} is required")
        if "points" in q:
            err.append(f"{at}: remove 'points' (Flooki assigns them and rejects questions that send them)")
        if "topic" in q and (not _text(q["topic"]) or len(q["topic"]) > 80):
            err.append(f"{at}: topic must be a non-empty string of at most 80 characters")
        if "img" in q:
            img = q["img"]
            if not isinstance(img, str) or not (re.match(r"^\s*<svg[\s>]", img) and img.rstrip().endswith("</svg>")
                                                 or MERMAID.match(img)):
                err.append(f"{at}: img must be inline <svg>…</svg> or Mermaid code (links and base64 are ignored)")
            elif "<svg" in img:
                try:   # Flooki shows SVG through <img src="data:…">, which needs strict XML
                    ET.fromstring(img)
                except ET.ParseError as x:
                    err.append(f"{at}: img SVG is not well-formed XML ({x}); Flooki would show a broken image")
                if "href=" in img or "<image" in img:
                    warn.append(f"{at}: img links to something outside the SVG; Flooki will not load it")
        if t == "short_answer":
            if not _text(q.get("correctAnswer")):
                err.append(f"{at}: correctAnswer is required")
            for k in ("options", "correctIndex"):
                if k in q:
                    err.append(f"{at}: short_answer must not have {k}")
        else:
            opts, ci = q.get("options"), q.get("correctIndex")
            if not isinstance(opts, list) or len(opts) < 2 or not all(_text(o) for o in opts):
                err.append(f"{at}: options must be at least 2 non-empty strings")
                opts = []
            if t == "true_false" and len(opts) != 2:
                err.append(f"{at}: true_false needs exactly 2 options")
            if type(ci) is not int or not 0 <= ci < len(opts):
                err.append(f"{at}: correctIndex must be a number from 0 to {len(opts) - 1}")
            if "correctAnswer" in q:
                err.append(f"{at}: choice questions must not have correctAnswer")
            if t == "multiple_choice" and 0 < len(opts) < 4:
                warn.append(f"{at}: only {len(opts)} options (Flooki recommends 4 or more)")
            normed = [re.sub(r"\s+|\$|\\[,;! ]", "", o.lower()) for o in opts]
            if len(set(normed)) < len(normed):
                warn.append(f"{at}: two options are the same")
        for k in ("text", "explanation", "correctAnswer", "topic"):
            v = q.get(k)
            if isinstance(v, str):
                if not _dollars_balanced(v):
                    warn.append(f"{at}: {k} has an odd number of $ (math left open)")
                if SOURCE_TALK.search(v):
                    warn.append(f"{at}: {k} mentions its source ({SOURCE_TALK.search(v)[0]!r}); questions must stand alone")
                if re.search(r"\\\(|\\\[", v):
                    warn.append(f"{at}: {k} uses \\( \\) or \\[ \\]; Flooki renders $…$ and $$…$$")
        opts, ci = q.get("options") or [], q.get("correctIndex")
        answer = q.get("correctAnswer") or (opts[ci] if type(ci) is int and 0 <= ci < len(opts) else "")
        sig = _norm(q.get("text", "")) + "|" + _norm(str(answer))
        for s, j in seen:
            if difflib.SequenceMatcher(None, sig, s).ratio() > 0.9:
                warn.append(f"{at}: nearly the same as Q{j}")
                break
        seen.append((sig, i))

    mc = [q for q in qs if q.get("type") == "multiple_choice" and type(q.get("correctIndex")) is int]
    if len(mc) >= 6:
        counts = [sum(q["correctIndex"] == k for q in mc) for k in range(4)]
        if max(counts) > 0.45 * len(mc):
            warn.append(f"answer positions are predictable (A–D: {counts}); run `shuffle`")
    return err, warn


def summary(exam: dict) -> str:
    qs = exam["questions"]
    kinds = {t: sum(q.get("type") == t for q in qs) for t in sorted(TYPES)}
    topics = {}
    for q in qs:
        topics[q.get("topic", "(no topic)")] = topics.get(q.get("topic", "(no topic)"), 0) + 1
    return (f"{len(qs)} questions: " + ", ".join(f"{n} {t}" for t, n in kinds.items() if n)
            + f"; {len(topics)} topics; {sum('img' in q for q in qs)} with a figure")


# ------------------------------------------------------------------ commands

def cmd_check(args) -> int:
    bad = 0
    for p in args.files:
        exam = load(p)
        err, warn = check(exam)
        print(f"{p.name}: {summary(exam) if isinstance(exam.get('questions'), list) else ''}")
        for e in err:
            print(f"  error: {e}")
        for w in warn:
            print(f"  warning: {w}")
        if not err and not warn:
            print("  ok")
        bad += bool(err)
    return 1 if bad else 0


def cmd_show(args) -> int:
    exam = load(args.file)
    print(f"# {exam['title']}\n{exam.get('description', '')}\n{json.dumps(exam.get('metadata', {}), ensure_ascii=False)}\n")
    for i, q in enumerate(exam["questions"], 1):
        print(f"--- Q{i} · {q.get('type')} · {q.get('topic', '')}" + (f" · source: {q['source']}" if q.get("source") else ""))
        print(q.get("text", ""))
        if q.get("img"):
            print("[figure: " + ("SVG" if "<svg" in q["img"] else "Mermaid") + "]")
        for j, o in enumerate(q.get("options") or []):
            print(f"  {'*' if j == q.get('correctIndex') else ' '} {'ABCDEFGH'[j]}. {o}")
        if q.get("correctAnswer"):
            print(f"  answer: {q['correctAnswer']}")
        print("  explanation: " + q.get("explanation", "").replace("\n", "\n    ") + "\n")
    print(summary(exam))
    return 0


def cmd_shuffle(args) -> int:
    """Shuffle each multiple-choice question's options so the right answers spread evenly over A, B, C, …
    (seeded, so it is repeatable). Options such as "All of the above" stay last."""
    exam = load(args.file)
    rng = random.Random(args.seed or exam["title"])
    mc = [q for q in exam["questions"] if q.get("type") == "multiple_choice" and type(q.get("correctIndex")) is int]
    width = max((len(q["options"]) for q in mc), default=1)
    targets = [i % width for i in range(len(mc))]   # each position about equally often, in random order
    rng.shuffle(targets)
    for q, target in zip(mc, targets):
        opts, right = q["options"], q["correctIndex"]
        fixed = [j for j, o in enumerate(opts) if KEEP_LAST.search(o)]
        free = [j for j in range(len(opts)) if j not in fixed]
        if right in fixed:   # the answer is "All of the above": it stays where it is
            others = free[:]
            rng.shuffle(others)
            order = others + fixed
        else:
            others = [j for j in free if j != right]
            rng.shuffle(others)
            t = target if target < len(free) else rng.randrange(len(free))
            order = others[:t] + [right] + others[t:] + fixed
        q["options"] = [opts[j] for j in order]
        q["correctIndex"] = order.index(right)
    moved = len(mc)
    save(args.file, exam)
    counts = [sum(q["correctIndex"] == k for q in mc) for k in range(max((len(q["options"]) for q in mc), default=0))]
    print(f"shuffled {moved} questions; correct answers now at A, B, C, …: {counts}")
    return 0


def cmd_payload(args) -> int:
    print(json.dumps(body(load(args.file)), ensure_ascii=False, indent=2))
    return 0


def from_env_file(path: Path) -> str:
    """FLOOKI_SERVICE_TOKEN=… from a dotenv file (quotes and `export ` allowed)."""
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*(?:export\s+)?FLOOKI_SERVICE_TOKEN\s*=\s*(.*)$", line)
        if m:
            return m[1].strip().strip("'\"")
    return ""


def token(path: Path | None, env_file: Path | None = None) -> str:
    t = os.environ.get("FLOOKI_SERVICE_TOKEN", "").strip()
    if not t and env_file:
        t = from_env_file(env_file)
    if not t:
        f = path or TOKEN_FILE
        if f.exists():
            t = f.read_text(encoding="utf-8").strip()
    if not t:
        raise SystemExit("no Flooki token. Set FLOOKI_SERVICE_TOKEN, pass --env-file with a .env that defines it, or save it\n"
                         "(copied to the clipboard) with:\n"
                         "  mkdir -p ~/.config/flooki && pbpaste > ~/.config/flooki/token && chmod 600 ~/.config/flooki/token")
    return t


def post(b: dict, tok: str) -> dict:
    data = json.dumps(b, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(API, data=data, method="POST", headers={
        "Authorization": f"Bearer {tok}", "Content-Type": "application/json", "User-Agent": "flooki-exam-skill/1"})
    for attempt in range(TRIES):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                code = json.loads(e.read().decode("utf-8")).get("error", "")
            except Exception:
                code = ""
            if e.code >= 500 and attempt < TRIES - 1:
                time.sleep(2 ** attempt * 2)
                continue
            raise SystemExit(f"Flooki said HTTP {e.code} {code}: {ERRORS.get(code, 'see reference/api.md')}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == TRIES - 1:
                raise SystemExit(f"network error after {TRIES} tries: {e}")
            time.sleep(min(2 ** attempt * 2, 20))
    raise SystemExit("unreachable")


def cmd_publish(args) -> int:
    exams = []
    for p in args.files:
        exam = load(p)
        err, warn = check(exam)
        if err:
            print(f"{p.name}: not sent, {len(err)} error(s); run `check`")
            return 1
        b = body(exam)
        sha = digest(b)
        done = exam.get("published") or {}
        if done.get("sha") == sha and not args.again:
            print(f"{p.name}: already published, unchanged: {done['url']}")
            continue
        if done and not args.again:
            print(f"{p.name}: changed since it was published ({done.get('url')}). Flooki cannot edit an exam: "
                  f"--again publishes a new one with a new link")
            return 1
        exams.append((p, exam, b, sha, len(warn)))
    if args.dry_run:
        for p, exam, b, sha, nw in exams:
            print(f"{p.name}: would send {summary(exam)}, {len(json.dumps(b)) // 1024} KB, {nw} warning(s)")
        return 0
    tok = token(args.token_file, args.env_file) if exams else ""
    for p, exam, b, sha, _ in exams:
        res = post(b, tok)
        if not res.get("url"):
            raise SystemExit(f"{p.name}: unexpected answer {res}")
        history = exam.get("published_before", [])
        if exam.get("published"):
            history.append(exam["published"])
            exam["published_before"] = history
        exam["published"] = {"id": res.get("id"), "url": res["url"], "sha": sha, "questions": len(exam["questions"]),
                             "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        save(p, exam)
        print(f"{p.name}: {res['url']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("check"); s.add_argument("files", nargs="+", type=Path); s.set_defaults(fn=cmd_check)
    s = sub.add_parser("show"); s.add_argument("file", type=Path); s.set_defaults(fn=cmd_show)
    s = sub.add_parser("shuffle"); s.add_argument("file", type=Path); s.add_argument("--seed"); s.set_defaults(fn=cmd_shuffle)
    s = sub.add_parser("payload"); s.add_argument("file", type=Path); s.set_defaults(fn=cmd_payload)
    s = sub.add_parser("publish"); s.add_argument("files", nargs="+", type=Path)
    s.add_argument("--dry-run", action="store_true", help="check and report, send nothing")
    s.add_argument("--again", action="store_true", help="publish even if already published (makes a new link)")
    s.add_argument("--token-file", type=Path, help=f"default: $FLOOKI_SERVICE_TOKEN, then {TOKEN_FILE}")
    s.add_argument("--env-file", type=Path, help="a .env file that defines FLOOKI_SERVICE_TOKEN")
    s.set_defaults(fn=cmd_publish)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
