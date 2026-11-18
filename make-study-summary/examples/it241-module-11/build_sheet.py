"""Build the IT241 Module 11 exam sheet from master.md: dark notebook page, soft highlighter markers, read-along markup.

    python3 build_sheet.py [master.md] [out.html]

Every narrated element has class="say". data-say is added only where the visible text has symbols or
abbreviations the voice would misread; it says the same words, with the symbols in words.
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import figs  # noqa: E402

D = Path(__file__).parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else D / "master.md"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / "dev/y3f/2026-fall/it241/exam-sheets/module-11/index.html"

# The key phrase to highlight in written-answer sentences (chosen by hand; the wording is unchanged).
KEYS = [
    "Time, date and user identification", "Knowing the file size in advance", "External fragmentation",
    "create, write, read, reposition (seek), delete and truncate",
    "Open and close", "moves the entry to memory", "back to the directory structure on disk",
    "still points to a file after the file was deleted", "Allow only links to files", "cycle detection algorithm",
    "Garbage collection", "Owner, group, public", "read, write and execute (r, w, x)",
    "organize and manage data storage", "mapping logical to physical", "stored, located and retrieved",
    "information about one file", "Permissions; size; pointers to the file's data blocks",
    "one entry in the system-wide open-file table", "one entry in its per-process open-file table",
    "Attaching a file system to the directory structure", "mount table records", "suffers from external fragmentation",
    "do not have external fragmentation", "internal fragmentation in the last block", "Finding space",
    "many I/Os and disk seeks", "space on a pointer", "A table at the beginning of the volume",
    "faster on disk and cacheable", "its own index block", "one bit for each disk block",
    "the first free block and the count", "used and freed in contiguous runs", "addresses of the next n−1 free blocks",
]
GOOD = re.compile(r"^(Advantages?|Pros?)$", re.I)
BAD = re.compile(r"^(Disadvantages?|Drawbacks?|Problems?|Issues?)$", re.I)

# ------------------------------------------------------------------ spoken forms
WORDS = {  # whole-word replacements for the voice
    "I/O": "I O", "I/Os": "I Os", "FCB": "F C B", "FCBs": "F C Bs", "NTFS": "N T F S", "UFS": "U F S", "ufs": "U F S",
    "FFS": "F F S", "ZFS": "Z F S", "zfs": "Z F S", "ACL": "A C L", "ACLs": "A C Ls", "OS": "O S", "OSs": "operating systems",
    "ISO": "I S O", "CD": "C D", "DVD": "D V D", "FAT32": "fat 32", "FAT": "fat", "ext3": "ext 3", "ext4": "ext 4",
    "tmpfs": "temp F S", "procfs": "proc F S", "objfs": "obj F S", "ctfs": "C T F S", "lofs": "lo F S",
    "GoogleFS": "Google F S", "ASM": "A S M", "FUSE": "fuse", "cp": "C P", "mkdir": "make dir", "chmod": "C H mod",
    "chgrp": "change group", "inode": "I node", "inodes": "I nodes", "rwx": "R W X", "RAID": "raid", "MIPS": "mips",
    "IOPS": "I O P S", "SSD": "S S D", "HDD": "H D D", "CPU": "C P U", "CPUs": "C P Us", "MFT": "M F T", "UNIX": "unix", "VMS": "V M S",
    "B+": "B plus", "KB": "kilobytes", "MB": "megabytes", "GB": "gigabytes", "TB": "terabytes", "vs": "versus", "metaslab": "meta slab", "metaslabs": "meta slabs", "Metaslabs": "Meta slabs",
    "dir-name": "dir name", "e.g.": "for example", "i.e.": "that is",
}


def spoken(t):
    t = t.replace("**", "").replace("★", "").strip()
    t = re.sub(r"(\d)\^(\d+)", r"\1 to the power \2", t)
    t = re.sub(r"\b[01]{8,}\b", lambda m: " ".join("one" if c == "1" else "zero" for c in m.group(0)), t)
    t = re.sub(r"(?<![\w/])/(\w+)/(\w+)", r"slash \1 slash \2", t)  # /user1/test
    t = re.sub(r"\(r, w, x\)", "(R, W, X)", t)
    t = t.replace("(s)", "s").replace("(lib, a, so, dll)", "(lib, A, S O, D L L)").replace("(obj, o)", "(obj, O)")
    t = re.sub(r"\b([rwx]) =", lambda m: m.group(1).upper() + " =", t)
    t = re.sub(r"(?<![\w-])([r-][w-][x-])([r-][w-][x-])([r-][w-][x-])(?![\w-])", r"\1 \2 \3", t)
    t = re.sub(r"(?<![\w-])([r-][w-][x-])(?![\w-])", lambda m: " ".join({"r": "R", "w": "W", "x": "X", "-": "dash"}[c] for c in m.group(1)), t)
    t = re.sub(r"\b([QR])(\d)\b", r"\1 \2", t)
    for k in sorted(WORDS, key=len, reverse=True):
        t = re.sub(rf"(?<![\w+]){re.escape(k)}(?![\w+])", WORDS[k], t)
    t = re.sub(r"(\w)/(\w)", r"\1, \2", t)  # owner/group/ACL
    t = re.sub(r"(\d)K\b", r"\1 K", t)
    t = (t.replace("÷", " divided by ").replace("×", " times ").replace("≈", " about ").replace("=", " equals ")
          .replace(" + ", " plus ").replace("−", " minus ").replace("&", " and ").replace("%", " percent")
          .replace("…", ", ").replace("·", ", "))
    t = re.sub(r"\((\d+), (\d+)\)(, )?", lambda m: f"{m.group(1)}, {m.group(2)}" + ("; " if m.group(3) else ""), t)  # (2, 4), (8, 6): pairs
    t = re.sub(r"\s*\(([^()]*)\)", r", \1,", t)  # parentheses become a short pause
    t = re.sub(r",\s*([.;:?!])", r"\1", t)
    t = re.sub(r",\s*,", ",", t)
    t = re.sub(r"\s+", " ", t).strip(" ,")
    if t and t[-1] not in ".?!:":
        t += "."
    return t


def visible(t):
    t = t.replace("**", "").replace("★", "").strip()
    return re.sub(r"\s+", " ", t)


def say(raw, role=None, cls=""):
    """Attributes for a narrated element: data-say only when the spoken form differs from what is shown."""
    sp, vis = spoken(raw), visible(raw)
    a = f' class="{(cls + " say").strip()}"'
    if sp.rstrip(".") != vis.rstrip("."):
        a += f' data-say="{html.escape(sp)}"'
    if role:
        a += f' data-role="{role}"'
    return a


# ------------------------------------------------------------------ markup
def esc(s):
    return html.escape(s, quote=False)


def fmt(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(\d)\^(\d+)", r"\1<sup>\2</sup>", s)
    return s.replace("★", '<span class="star" title="Asked on a past final">★</span>')


def mark(text, colour):
    inner = re.sub(r"(\([^()]*\))", r'<span class="aside">\1</span>', fmt(text))
    return f'<mark class="{colour}">{inner}</mark>'


def split_core(a):
    depth, cut = 0, len(a)
    for i, ch in enumerate(a):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0 and ch in ".;:" and (i + 1 == len(a) or a[i + 1] == " "):
            cut = i
            break
    core = a[:cut]
    if len(re.sub(r"\(.*?\)", "", core).split()) > 9:
        m = re.search(r", (so|provided|kept|while|which|because) ", core)
        if m:
            cut = m.start()
            core = a[:cut]
    return core, a[cut:]


def bullet(x, calc):
    x = x.strip()
    m = re.match(r"^Answer:\s*(.+)$", x)
    if m:
        return (f'<li{say(x, cls="final")}><span class="lbl">Answer</span> '
                f'{mark(m.group(1).rstrip("."), "b")}</li>')
    m = re.match(r"^([^:]{1,40}):\s+(.+)$", x)
    if m and len(m.group(1).split()) <= 5 and not re.search(r"\d\s*[=÷×]", m.group(1)):
        lab, rest = m.group(1), m.group(2)
        if GOOD.match(lab):
            return f'<li{say(x)}><span class="lbl good">{esc(lab)}</span> {fmt(rest)}</li>'
        if BAD.match(lab):
            return f'<li{say(x)}><span class="lbl bad">{esc(lab)}</span> {fmt(rest)}</li>'
        return f"<li{say(x)}>{mark(lab, 'y soft')}: {fmt(rest)}</li>"
    k = next((k for k in KEYS if k in x), None) if not calc else None
    if k:
        a, b = x.split(k, 1)
        return f"<li{say(x)}>{fmt(a)}{mark(k, 'y soft')}{fmt(b)}</li>"
    if not calc and len(x.rstrip(".").split()) <= 4 and not x.startswith("("):
        return f"<li{say(x)}>{mark(x.rstrip('.'), 'y soft')}</li>"
    return f'<li{say(x, cls="work" if calc else "")}>{fmt(x)}</li>'


LABEL = {"Key terms": "terms", "Rules": "rules", "Written questions": "written", "Calculations": "calc", "Traps": "traps"}


def drop_empty_blocks(lines):
    """A block heading with no items under it is left out."""
    return [l for i, l in enumerate(lines)
            if not (l.startswith("### ") and (i + 1 == len(lines) or lines[i + 1].startswith(("## ", "### ")) or not lines[i + 1].strip()))]


def build(lines):
    lines = drop_empty_blocks(lines)
    out, nav, block, i, open_blk, topic = [], [], None, 0, None, None

    def close():
        nonlocal open_blk
        if open_blk:
            out.append("</dl></div>" if open_blk == "terms" else "</div>")
            open_blk = None

    while i < len(lines):
        l = lines[i]
        if l.startswith("## "):
            close()
            if out:
                out.append("</section>")
            num, title = l[3:].split(". ", 1)
            nav.append(f'<a href="#t{num}"><span>{int(num):02d}</span>{esc(title)}</a>')
            out.append(f'<section class="topic" id="t{num}"><header class="th"><span class="tn" aria-hidden="true">{int(num):02d}</span>'
                       f'<h2 class="say" data-say="{num}. {html.escape(spoken(title))}">{esc(title)}</h2></header>' + "".join(figs.TOPIC.get(num, [])))
            topic = num
        elif l.startswith("### "):
            close()
            block = l[4:]
            kind = LABEL[block]
            out.append(f'<div class="blk {kind}" data-box="{kind}"><h3 class="say"><i aria-hidden="true"></i>{esc(block)}</h3>'
                       + ("<dl>" if kind == "terms" else "")
                       + ("".join(figs.CALC.get(topic, [])) if kind == "calc" else ""))
            open_blk = kind
        elif l.startswith("**Q."):
            q = l.strip("*")[3:].strip()
            j = i + 1
            while j < len(lines) and lines[j].startswith("- "):
                j += 1
            lis = "".join(bullet(x[2:], block == "Calculations") for x in lines[i + 1:j])
            out.append(f'<div class="wq"><p{say(q, "question", "q")}>{fmt(q)}</p><ul class="a">{lis}</ul></div>')
            i = j
            continue
        elif l.startswith("- **"):
            m = re.match(r"- \*\*(.+?)\*\*:? ?(.*)$", l)
            head, rest = m.group(1), m.group(2)
            if block == "Key terms":
                star = ""
                if head.startswith("★"):
                    star, head = fmt("★") + " ", head[1:].strip()
                out.append(f'<dt{say(head, "term")}>{star}{mark(head, "y")}</dt><dd{say(rest)}>{fmt(rest)}</dd>')
            else:
                colour = "p" if block == "Traps" else "g"
                core, tail = split_core(rest.strip())
                out.append(f'<div class="qa"><p{say(head, "question", "q")}>{fmt(head)}</p>'
                           f'<p{say(rest, cls="a")}>{mark(core, colour)}{fmt(tail)}</p></div>')
        else:
            sys.exit(f"unplaced line: {l}")
        i += 1
    close()
    out.append("</section>")
    return "".join(nav), "\n".join(out)


PAGE = """<!DOCTYPE html>
<html lang="en" class="ra-dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#000000">
<title>File Systems · IT241 exam sheet</title>
<script>document.documentElement.classList.add('ra-dark')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:ital,wght@0,400;0,600;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{
  --k-bg:#000; --k-panel:#0e0e0f; --k-edge:rgba(255,255,255,.1);
  --k-text:#dcdcdc; --k-strong:#f5f5f5; --k-muted:#9b9b9b; --k-faint:#626262;
  --y:255,206,64; --g:72,222,150; --b:98,186,255; --p:255,108,162; --k-star:#ff9470;
  --k-read:"Atkinson Hyperlegible Next","Atkinson Hyperlegible",system-ui,sans-serif;
  --k-display:"Bricolage Grotesque","Avenir Next",system-ui,sans-serif;
  --k-mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
  --k-w:940px;
}
html.ra-dark:root{--ra-hl:rgba(150,180,255,.15);--ra-hover:rgba(255,255,255,.05)}
html.ra-dark .ra{background:rgba(18,18,19,.96)}
.ra-switch{display:none!important}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;color:var(--k-text);font:400 18.5px/1.8 var(--k-read);
  background:var(--k-bg)}
a{color:inherit}
:focus-visible{outline:2px solid rgb(var(--b));outline-offset:3px;border-radius:4px}

/* hero */
#top{max-width:var(--k-w);margin:0 auto;padding:56px 28px 8px}
.kicker{font:500 12.5px var(--k-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--k-muted);margin:0 0 22px;display:flex;justify-content:space-between;gap:12px}
.kicker a{text-decoration:none;color:var(--k-muted)} .kicker a:hover{color:var(--k-strong)}
h1{font:800 clamp(46px,9vw,80px)/.95 var(--k-display);letter-spacing:-.03em;color:var(--k-strong);margin:0}
.sub{font:600 clamp(17px,2.6vw,20px)/1.45 var(--k-display);color:var(--k-muted);margin:16px 0 0}
#top .legend{margin:34px 0 0;padding:22px 26px;background:var(--k-panel);border:1px solid var(--k-edge);border-radius:18px;font-size:17px;line-height:2.1;color:var(--k-text)}
#top .legend p{margin:0}
#top .legend p+p{margin-top:6px;color:var(--k-muted);font-size:16px;line-height:1.6}
.toc{display:flex;flex-wrap:wrap;gap:8px 8px;margin:28px 0 0;padding:0;list-style:none}
.toc a{display:inline-block;text-decoration:none;font:600 15px var(--k-read);color:var(--k-muted);padding:7px 14px;border:1px solid var(--k-edge);border-radius:999px}
.toc a span{font:700 12px var(--k-mono);color:rgb(var(--y));margin-right:8px}
.toc a:hover{color:var(--k-strong);border-color:rgba(255,255,255,.28)}

/* topics */
#sheet{max-width:var(--k-w);margin:0 auto;padding:0 28px 140px}
#sheet .topic{padding-top:120px}
#sheet .th{display:flex;align-items:baseline;gap:16px;margin-bottom:8px;padding-bottom:18px;border-bottom:1px solid var(--k-edge)}
#sheet .tn{font:700 16px var(--k-mono);color:rgb(var(--y));letter-spacing:.04em}
#sheet h2{font:800 clamp(32px,5.4vw,44px)/1.1 var(--k-display);letter-spacing:-.02em;color:var(--k-strong);margin:0}
#sheet .blk{margin-top:60px}
#sheet h3{display:flex;align-items:center;gap:11px;font:700 13px var(--k-mono);letter-spacing:.16em;text-transform:uppercase;color:var(--k-muted);margin:0 0 24px}
#sheet h3 i{width:10px;height:10px;border-radius:3px;background:var(--k-faint)}
#sheet .terms h3 i{background:rgb(var(--y))} #sheet .rules h3 i{background:rgb(var(--g))} #sheet .calc h3 i{background:rgb(var(--b))}
#sheet .traps h3 i{background:rgb(var(--p))} #sheet .written h3 i{background:var(--k-strong)}

/* key terms */
#sheet dl{margin:0}
#sheet dt{font:700 19px/1.5 var(--k-read);color:var(--k-strong);margin-top:34px}
#sheet dt:first-child{margin-top:0}
#sheet dd{margin:8px 0 0;color:var(--k-text)}

/* rules and traps */
#sheet .qa+.qa{margin-top:34px}
#sheet .q{margin:0;color:var(--k-muted);font-size:17px;line-height:1.6}
#sheet .qa .a{margin:8px 0 0;color:var(--k-text)}
#sheet .traps{background:linear-gradient(90deg,rgba(var(--p),.075),rgba(var(--p),.015) 70%);border-left:3px solid rgba(var(--p),.75);border-radius:4px 18px 18px 4px;padding:26px 28px}

/* written and calculations */
#sheet .wq{background:var(--k-panel);border:1px solid var(--k-edge);border-radius:18px;padding:24px 28px 20px}
#sheet .wq+.wq{margin-top:22px}
#sheet .wq .q{color:var(--k-strong);font-weight:700;font-size:18px;line-height:1.55}
#sheet .wq .a{margin:14px 0 0;padding:0;list-style:none}
#sheet .wq .a li{position:relative;padding-left:24px;margin:10px 0}
#sheet .wq .a li::before{content:"";position:absolute;left:4px;top:.78em;width:7px;height:7px;border-radius:50%;border:1.5px solid var(--k-faint)}
#sheet .calc .wq{border-color:rgba(var(--b),.2)}
#sheet .calc .a li.work{font-variant-numeric:tabular-nums}
#sheet .a li.final{margin-top:16px} #sheet .a li.final::before{border-color:rgb(var(--b));background:rgb(var(--b))}
#sheet .lbl{font:700 12px var(--k-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--k-muted);margin-right:6px}
#sheet .lbl.good{color:rgb(var(--g))} #sheet .lbl.bad{color:rgb(var(--p))}

/* the highlighter: a soft, full-height swipe behind the words, one colour per meaning */
#top mark,#sheet mark{font-weight:600;padding:.06em .3em;margin:0 -.04em;border-radius:.3em .5em .34em .46em;border:0;text-decoration:none;
  background:linear-gradient(100deg,rgba(var(--mk),.15),rgba(var(--mk),.23) 45%,rgba(var(--mk),.17));
  -webkit-box-decoration-break:clone;box-decoration-break:clone}
#top mark.y,#sheet mark.y{--mk:var(--y);color:#fdf0c8} #top mark.g,#sheet mark.g{--mk:var(--g);color:#d2f7e4}
#top mark.b,#sheet mark.b{--mk:var(--b);color:#d6ebff} #top mark.p,#sheet mark.p{--mk:var(--p);color:#ffd9e6}
#sheet mark.soft{background:linear-gradient(100deg,rgba(var(--mk),.1),rgba(var(--mk),.16) 45%,rgba(var(--mk),.11))}
#sheet mark .aside{font-weight:400;opacity:.8}
.star{color:var(--k-star);font-size:.95em}

footer{max-width:var(--k-w);margin:0 auto;padding:0 28px 60px;color:var(--k-faint);font:500 13px var(--k-mono)}

@media (max-width:640px){
  body{font-size:17.5px}
  #top{padding:32px 16px 4px} #sheet{padding:0 16px 120px} footer{padding:0 16px 48px}
  #sheet .topic{padding-top:88px} #sheet .blk{margin-top:48px}
  #sheet .wq{padding:20px 18px 16px} #sheet .traps{padding:20px 18px}
  #top .legend{padding:18px}
}
""" + figs.CSS + """</style>
</head>
<body>
""" + figs.DEFS + """
<header id="top">
<p class="kicker"><span>IT241 · Final exam sheet</span><a href="../../">IT241 course page</a></p>
<h1>File Systems</h1>
<p class="sub">Module 11. Nine topics, each in the same order: key terms, rules, written questions, calculations, traps.</p>
<div class="legend">
<p><mark class="y">Yellow</mark> the term &nbsp; <mark class="g">Green</mark> the answer to say &nbsp; <mark class="b">Blue</mark> the result &nbsp; <mark class="p">Pink</mark> the trap &nbsp; <span class="star">★</span> asked on a past final</p>
<p>Press play at the bottom to listen. Tap any line to start from there.</p>
</div>
<nav aria-label="Topics"><ul class="toc">{{NAV}}</ul></nav>
</header>
<main id="sheet">
{{BODY}}
</main>
<footer>IT241 Operating Systems · Module 11 · File Systems and File-System Implementation</footer>
</body>
</html>
"""


if __name__ == "__main__":
    nav, body = build(SRC.read_text().splitlines())
    nav = "".join(f"<li>{a}</li>" for a in re.findall(r"<a .*?</a>", nav))
    OUT.write_text(PAGE.replace("{{NAV}}", nav).replace("{{BODY}}", body))
    print(OUT, "·", body.count("<mark"), "markers ·", len(re.findall(r'class="[^"]*\bsay\b', body)), "narrated")
