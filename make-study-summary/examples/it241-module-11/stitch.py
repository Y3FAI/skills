"""Stitch Gemini's first full sheet (r1, rendered text) with its change list (r2) into master.md, then build the page.

    python3 stitch.py            # writes master.md and the y3f page
"""
import html
import re
import sys
from pathlib import Path

D = Path(__file__).parent
PAGE = Path.home() / "dev/y3f/2026-fall/it241/exam-sheets/module-11/index.html"  
TOPICS = ["Files", "Access methods", "Disks, volumes and many file systems", "Directories", "Protection",
          "File-system structure", "Implementation structures", "Allocation methods", "Free-space management"]
BLOCKS = ["Key terms", "Rules", "Written questions", "Calculations", "Traps"]
# Gemini's new traps that repeat a rule or a written question: keep one copy only.
DUPES = ["Which problem does a two-level directory solve?", "What does deleting a directory remove?",
         "What is the difference between truncate and delete?"]


def norm(s):
    s = re.sub(r"^\s*-\s*", "", s.strip()).replace("**", "")
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- r1 to master lines
def parse_r1(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    out, block = [], None
    for l in lines:
        m = re.match(r"^(\d)\. (.+)$", l)
        if m and m.group(2) in TOPICS:
            out.append(f"## {l}"); block = None; continue
        if l in BLOCKS:
            out.append(f"### {l}"); block = l; continue
        if l.startswith(("Reorganized the document", "Integrated all verified")):
            break
        if block == "Key terms":
            term, meaning = l.split(": ", 1)
            out.append(f"- **{term}**: {meaning}")
        elif block in ("Rules", "Traps"):
            if "? " not in l:
                sys.exit(f"no question mark: {l}")
            q, a = l.split("? ", 1)
            out.append(f"- **{q}?** {a}")
        elif l.startswith("Q. "):
            out.append(f"**{l}**")
        else:
            out.append(f"- {l}")
    return out


# ---------------------------------------------------------------- r2 changes
def parse_r2(text):
    body = text.split("\n", 1)[1] if text.startswith("Plaintext") else text
    body = body.rsplit("I made", 1)[0]
    reps, adds, i = [], [], 0
    L = body.splitlines()
    while i < len(L):
        l = L[i]
        if l.startswith("REPLACE:"):
            old = [l[8:].strip()] if l[8:].strip() else []
            i += 1
            while not L[i].startswith("WITH:"):
                if L[i].strip(): old.append(L[i])
                i += 1
            new = [L[i][5:].strip()] if L[i][5:].strip() else []
            i += 1
            while i < len(L) and L[i].strip() and not L[i].startswith(("REPLACE:", "ADD TO:")):
                new.append(L[i]); i += 1
            reps.append((old, new))
        elif l.startswith("ADD TO:"):
            topic, block = [x.strip() for x in l[7:].split("/")]
            i += 1; new = []
            while i < len(L) and not L[i].startswith(("REPLACE:", "ADD TO:")):
                if L[i].strip(): new.append(L[i])
                i += 1
            adds.append((topic, block, new))
        else:
            i += 1
    return reps, adds


def item_end(m, i):
    """Index after the item starting at i (a written question takes its answer lines)."""
    j = i + 1
    if m[i].startswith("**Q."):
        while j < len(m) and m[j].startswith("- "):
            j += 1
    return j


def find(m, old0):
    n = norm(old0)
    for i, l in enumerate(m):
        if norm(l) == n:
            return i
    q = n.split("?")[0]  # fall back to the question part (r1 lost text in angle brackets)
    hits = [i for i, l in enumerate(m) if "?" in n and norm(l).split("?")[0] == q]
    return hits[0] if len(hits) == 1 else None


def apply(m, reps, adds):
    for old, new in reps:
        i = find(m, old[0])
        if i is None:
            sys.exit(f"REPLACE not found: {old[0]}")
        j = item_end(m, i) if len(old) > 1 else i + 1
        m[i:j] = new
    for topic, block, new in adds:
        t = next(i for i, l in enumerate(m) if l == f"## {topic}")
        end = next((i for i in range(t + 1, len(m)) if m[i].startswith("## ")), len(m))
        b = next((i for i in range(t, end) if m[i] == f"### {block}"), None)
        if b is None:  # create the block in its place in the block order
            later = BLOCKS[BLOCKS.index(block) + 1:]
            pos = next((i for i in range(t, end) if m[i][4:] in later and m[i].startswith("### ")), end)
            m[pos:pos] = [f"### {block}"]
            b, end = pos, end + 1
        bend = next((i for i in range(b + 1, end) if m[i].startswith("### ")), end)
        m[bend:bend] = new
    # The only wording added by hand: the slide's example of an extent-based file system.
    for i, l in enumerate(m):
        if l.startswith("- **Extent**:") and "Veritas" not in l:
            m[i] = l.replace("(used in extent-based file systems)", "(used in extent-based file systems, such as Veritas)")
    for d in DUPES:
        traps = [i for i, l in enumerate(m) if norm(l).startswith(d)]
        for i in reversed(traps):
            del m[i]
    return m


# ---------------------------------------------------------------- page
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(\d)\^(\d+)", r"\1<sup>\2</sup>", s)
    return s.replace("★", '<span class="star">★</span>')


def build(m):
    parts, nav, i, in_traps = [], [], 0, False
    while i < len(m):
        l = m[i]
        if l.startswith("## "):
            if in_traps: parts.append("</div>"); in_traps = False
            num, title = l[3:].split(". ", 1)
            nav.append(f'<a href="#t{num}">{num} · {html.escape(title)}</a>')
            parts.append(f'\n<h2 id="t{num}">{num} · {html.escape(title)}</h2>')
        elif l.startswith("### "):
            if in_traps: parts.append("</div>"); in_traps = False
            parts.append(f"<h3>{l[4:]}</h3>")
            if l[4:] == "Traps":
                parts.append('<div class="traps">'); in_traps = True
        elif l.startswith("**Q."):
            q = l.strip("*")[3:].strip()
            j = item_end(m, i)
            lis = "".join(f"<li>{inline(x[2:])}</li>" for x in m[i + 1:j])
            parts.append(f'<div class="qa"><p class="q">{inline(q)}</p><div class="a"><ul>{lis}</ul></div></div>')
            i = j; continue
        elif l.startswith("- **"):
            mm = re.match(r"- \*\*(.+?)\*\*:? ?(.*)$", l)
            head, rest = mm.group(1), mm.group(2)
            cls = "qa" if head.endswith("?") else "qa term"
            parts.append(f'<div class="{cls}"><p class="q">{inline(head)}</p><p class="a">{inline(rest)}</p></div>')
        else:
            sys.exit(f"unplaced line: {l}")
        i += 1
    if in_traps: parts.append("</div>")
    tpl = (D / "page-template.html").read_text()
    return tpl.replace("{{NAV}}", "".join(nav)).replace("{{BODY}}", "\n".join(parts))


if __name__ == "__main__":
    master = apply(parse_r1((D / "r1.md").read_text()), *parse_r2((D / "r2.md").read_text()))
    (D / "master.md").write_text("\n".join(master) + "\n")
    PAGE.write_text(build(master))
    print("master lines", len(master), "· page written")
