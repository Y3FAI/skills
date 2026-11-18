"""Memory pictures for the Module 11 exam sheet: inline SVG, drawn in the sheet's marker colours.

Every number here comes from the sheet's own examples (mail at block 19, jeep's chain 9 16 1 10 25,
chmod 761, the 16-block bit vector, the counting list). Figures are silent in the read-along.
"""
from html import escape

W = 860
COL = {"y": "255,206,64", "g": "72,222,150", "b": "98,186,255", "p": "255,108,162"}

CSS = """
.viz{margin:48px 0 8px;}
.calc .viz{margin:0 0 28px;}
.viz{padding:26px 26px 18px;background:#070707;border:1px dashed rgba(255,255,255,.14);border-radius:20px}
.viz-in{overflow-x:auto;-webkit-overflow-scrolling:touch}
.viz svg{display:block;width:100%;height:auto;min-width:600px}
.viz figcaption{margin-top:14px;font:600 15px/1.5 var(--k-read);color:var(--k-muted)}
.viz figcaption b{font:700 11.5px var(--k-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--k-faint);margin-right:10px}
.viz text{font:500 14px var(--k-read);fill:#dcdcdc}
.viz .h{font-weight:700;font-size:15.5px;fill:#f5f5f5}
.viz .m{font-size:13px;fill:#9b9b9b}
.viz .mono{font-family:var(--k-mono);font-size:13px}
.viz .sm{font-size:11px}
.viz .big{font-size:22px;font-weight:700}
.viz .ty{fill:#fdf0c8} .viz .tg{fill:#d2f7e4} .viz .tb{fill:#d6ebff} .viz .tp{fill:#ffd9e6}
.viz .c-n{fill:#151516;stroke:rgba(255,255,255,.2);stroke-width:1.2}
.viz .c-raw{fill:none;stroke:rgba(255,255,255,.35);stroke-width:1.4;stroke-dasharray:5 4}
.viz .c-y{fill:rgba(255,206,64,.15);stroke:rgba(255,206,64,.6);stroke-width:1.3}
.viz .c-g{fill:rgba(72,222,150,.14);stroke:rgba(72,222,150,.6);stroke-width:1.3}
.viz .c-b{fill:rgba(98,186,255,.14);stroke:rgba(98,186,255,.6);stroke-width:1.3}
.viz .c-p{fill:rgba(255,108,162,.14);stroke:rgba(255,108,162,.6);stroke-width:1.3}
.viz .ln{fill:none;stroke-width:1.7}
.viz .s-n{stroke:#808080} .viz .s-y{stroke:rgb(255,206,64)} .viz .s-g{stroke:rgb(72,222,150)}
.viz .s-b{stroke:rgb(98,186,255)} .viz .s-p{stroke:rgb(255,108,162)}
.viz .dash{stroke-dasharray:5 4}
.viz .soft{opacity:.55}
@media (max-width:640px){.viz{padding:18px 14px 14px;margin-left:-4px;margin-right:-4px}}
"""

DEFS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
        + "".join(f'<marker id="a-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                  f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{v}"/></marker>'
                  for k, v in {"n": "#808080", "y": "rgb(255,206,64)", "g": "rgb(72,222,150)",
                               "b": "rgb(98,186,255)", "p": "rgb(255,108,162)"}.items())
        + "</defs></svg>")


# ------------------------------------------------------------------ drawing helpers
def T(x, y, s, cls="", a="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{a}">{escape(s)}</text>'


def R(x, y, w, h, cls="c-n", r=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{cls}"/>'


def L(x1, y1, x2, y2, c="n", arrow=True, dash=False, extra=""):
    m = f' marker-end="url(#a-{c})"' if arrow else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="ln s-{c}{" dash" if dash else ""} {extra}"{m}/>'


def P(d, c="n", arrow=True, dash=False):
    m = f' marker-end="url(#a-{c})"' if arrow else ""
    return f'<path d="{d}" class="ln s-{c}{" dash" if dash else ""}"{m}/>'


def tag(x, y, s, c):
    w = round(len(s) * 7.1 + 22)
    tc = {"n": "m", "y": "ty", "g": "tg", "b": "tb", "p": "tp"}[c]
    return R(x, y, w, 24, f"c-{c}", 12) + T(x + w / 2, y + 16.5, s, f"{tc} sm-tag", "middle")


def box(x, y, w, h, title, sub="", cls="c-n", tcls="h", a="middle"):
    tx = x + w / 2 if a == "middle" else x + 14
    out = R(x, y, w, h, cls)
    if sub:
        out += T(tx, y + h / 2 - 3, title, tcls, a) + T(tx, y + h / 2 + 15, sub, "m", a)
    else:
        out += T(tx, y + h / 2 + 5, title, tcls, a)
    return out


def fig(h, body, caption, label):
    return (f'<figure class="viz"><div class="viz-in"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{escape(label)}">'
            f"{body}</svg></div><figcaption><b>Picture it</b>{escape(caption)}</figcaption></figure>")


# ------------------------------------------------------------------ 1 · files: locks
def f_locks():
    o = [T(20, 28, "Shared lock", "h"), T(450, 28, "Exclusive lock", "h")]
    for i, y in enumerate((78, 133, 188)):
        o.append(f'<circle cx="62" cy="{y}" r="21" class="c-g"/>' + T(62, y + 5, f"P{i + 1}", "tg", "middle"))
        o.append(L(84, y, 246, 112 + i * 22, "g"))
    o.append(box(250, 88, 130, 92, "file", cls="c-y", tcls="h ty"))
    o.append(T(150, 72, "read", "tg m", "middle"))
    o.append(T(20, 236, "Many processes at once, like a reader lock.", "m"))
    o.append('<circle cx="492" cy="78" r="21" class="c-b"/>' + T(492, 83, "P1", "tb", "middle"))
    o.append(L(514, 82, 676, 120, "b") + T(590, 82, "write", "tb m", "middle"))
    for i, y in enumerate((133, 188)):
        o.append(f'<circle cx="492" cy="{y}" r="21" class="c-n"/>' + T(492, y + 5, f"P{i + 2}", "m", "middle"))
        o.append(L(514, y, 618, y, "p", arrow=False, dash=True) + T(632, y + 6, "✕", "tp h", "middle"))
    o.append(box(680, 88, 130, 92, "file", cls="c-y", tcls="h ty"))
    o.append(T(450, 236, "Only one process, like a writer lock.", "m"))
    o.append(L(20, 262, 840, 262, "n", arrow=False, dash=True, extra="soft"))
    o.append(T(20, 294, "Mandatory locking", "h"))
    o.append(box(20, 310, 110, 38, "process") + L(132, 329, 166, 329, "n"))
    o.append(box(170, 310, 130, 38, "OS denies", cls="c-p", tcls="h tp") + L(302, 329, 336, 329, "n", dash=True))
    o.append(box(340, 310, 80, 38, "file", cls="c-y", tcls="h ty"))
    o.append(T(450, 294, "Advisory locking", "h"))
    o.append(box(450, 310, 110, 38, "process") + L(562, 329, 606, 329, "g", dash=True) + T(584, 318, "checks", "tg sm", "middle"))
    o.append(box(610, 310, 130, 38, "lock status", cls="c-g", tcls="h tg"))
    o.append(T(752, 334, "then decides", "m"))
    return fig(370, "".join(o), "Shared means many readers; exclusive means one writer. Mandatory: the OS enforces the lock. Advisory: each process checks and decides.",
               "Shared and exclusive locks; mandatory and advisory locking")


# ------------------------------------------------------------------ 2 · access methods
def f_access():
    x0, w = 262, 56
    o = [T(20, 66, "Sequential", "h"), T(20, 88, "read next · write next · reset", "m")]
    for i in range(10):
        o.append(box(x0 + i * w + 2, 48, w - 4, 44, str(i), cls="c-g" if i == 3 else "c-n", tcls="mono"))
    for i in range(3):
        a, b = x0 + i * w + 40, x0 + (i + 1) * w + 18
        o.append(P(f"M{a},48 Q{(a + b) / 2},20 {b},48", "g"))
    o.append(T(x0 + w * 1.5 + 29, 18, "read next", "tg m", "middle"))
    cx = x0 + 3 * w + 29
    o.append(f'<path d="M{cx},98 l-7,12 h14 z" fill="rgb(72,222,150)"/>' + T(cx, 128, "cp", "tg h", "middle"))
    o.append(P(f"M{x0 + 3 * w + 12},92 Q{x0 + 110},168 {x0 + 29},96", "b", dash=True))
    o.append(T(x0 + 76, 160, "reset: cp = 0", "tb m", "middle"))
    o.append(T(20, 236, "Direct (relative)", "h"))
    o.append(T(20, 258, "read n · write n · position to n", "m"))
    for i in range(10):
        o.append(box(x0 + i * w + 2, 218, w - 4, 44, str(i), cls="c-b" if i == 7 else "c-n", tcls="mono"))
    o.append(L(x0 + 2, 282, x0 + 7 * w + 2, 282, "b"))
    o.append(L(x0 + 2, 274, x0 + 2, 290, "b", arrow=False))
    o.append(T(x0 + 3.5 * w, 306, "n = 7: a relative block number, counted from the start of the file", "tb m", "middle"))
    return fig(320, "".join(o), "Sequential moves one record at a time from cp; direct jumps straight to block n.",
               "Sequential access moves cp one block at a time; direct access jumps to block n")


# ------------------------------------------------------------------ 3 · disks and volumes
def f_disks():
    o = [T(20, 44, "Disk 1", "h"), R(20, 56, 400, 124, "c-n", 14)]
    o.append(R(32, 68, 228, 100, "c-y") + T(146, 102, "Partition A", "h ty", "middle")
             + T(146, 124, "formatted (cooked)", "m", "middle") + T(146, 144, "holds a file system: a volume", "m", "middle"))
    o.append(R(270, 68, 138, 100, "c-raw") + T(339, 102, "Partition B", "h", "middle")
             + T(339, 124, "raw", "m", "middle") + T(339, 144, "no file system", "m", "middle"))
    for x, n in ((460, 2), (660, 3)):
        o.append(T(x, 44, f"Disk {n}", "h") + R(x, 56, 180, 124, "c-b", 14) + T(x + 90, 124, "part of one volume", "tb m", "middle"))
    o.append(P("M460,194 v12 h380 v-12", "b", arrow=False))
    o.append(T(650, 230, "One volume across two disks", "tb h", "middle"))
    o.append(T(650, 252, "RAID protects disks against failure", "m", "middle"))
    o.append(T(20, 222, "partition = minidisk = slice", "h"))
    o.append(T(20, 246, "volume = the entity containing a file system", "m"))
    return fig(272, "".join(o), "A volume is whatever holds a file system: part of a disk, a whole disk, or several disks.",
               "Disk 1 with a formatted and a raw partition; one volume spanning disks 2 and 3")


# ------------------------------------------------------------------ 4 · directories
def dnode(x, y, s, w=70):
    return R(x - w / 2, y - 14, w, 28, "c-y", 7) + T(x, y + 5, s, "ty sm-n", "middle")


def fnode(x, y, s, cls="c-b", tc="tb"):
    return R(x - 24, y - 12, 48, 24, cls, 12) + T(x, y + 4.5, s, f"{tc} mono sm", "middle")


def edge(x1, y1, x2, y2):
    return L(x1, y1 + 14, x2, y2 - 13, "n", arrow=False)


def f_dirs():
    o = []
    # single-level
    ox = 20
    o.append(T(ox, 28, "Single-level", "h") + dnode(ox + 130, 66, "directory", 86))
    for i, s in enumerate(("cat", "bo", "a", "test", "data")):
        x = ox + 22 + 54 * i
        o.append(edge(ox + 130, 66, x, 132) + fnode(x, 132, s))
    o.append(tag(ox, 170, "naming problem", "p") + tag(ox, 200, "grouping problem", "p"))
    # two-level
    ox = 305
    o.append(T(ox, 28, "Two-level", "h") + dnode(ox + 135, 66, "master dir", 96))
    for ux, u, files in ((ox + 65, "user1", ("test", "data")), (ox + 205, "user2", ("test", "a"))):
        o.append(edge(ox + 135, 66, ux, 110) + dnode(ux, 110, u))
        for j, f in enumerate(files):
            fx = ux - 30 + 60 * j
            same = f == "test"
            o.append(edge(ux, 110, fx, 160) + fnode(fx, 160, f, "c-g" if same else "c-b", "tg" if same else "tb"))
    o.append(tag(ox, 200, "fixes naming", "g") + tag(ox + 125, 200, "no grouping", "p"))
    # tree
    ox = 590
    o.append(T(ox, 28, "Tree-structured", "h") + dnode(ox + 135, 66, "root"))
    o.append(edge(ox + 135, 66, ox + 60, 110) + dnode(ox + 60, 110, "spell"))
    o.append(edge(ox + 135, 66, ox + 205, 110) + dnode(ox + 205, 110, "mail"))
    o.append(edge(ox + 60, 110, ox + 30, 160) + fnode(ox + 30, 160, "list"))
    o.append(edge(ox + 60, 110, ox + 90, 160) + fnode(ox + 90, 160, "obj"))
    o.append(edge(ox + 205, 110, ox + 170, 160) + dnode(ox + 170, 160, "prog", 58))
    o.append(edge(ox + 205, 110, ox + 240, 160) + fnode(ox + 240, 160, "copy"))
    o.append(tag(ox, 200, "adds grouping", "g") + tag(ox + 132, 200, "no sharing", "p"))
    o.append(L(20, 246, 840, 246, "n", arrow=False, dash=True, extra="soft"))
    # acyclic
    ox, y0 = 90, 250
    o.append(T(ox, y0 + 30, "Acyclic graph", "h") + dnode(ox + 150, y0 + 66, "root"))
    o.append(edge(ox + 150, y0 + 66, ox + 70, y0 + 112) + dnode(ox + 70, y0 + 112, "dict"))
    o.append(edge(ox + 150, y0 + 66, ox + 230, y0 + 112) + dnode(ox + 230, y0 + 112, "spell"))
    o.append(edge(ox + 70, y0 + 112, ox + 150, y0 + 164) + edge(ox + 230, y0 + 112, ox + 150, y0 + 164))
    o.append(fnode(ox + 150, y0 + 164, "list", "c-g", "tg") + T(ox + 186, y0 + 168, "one shared file", "tg m"))
    o.append(tag(ox, y0 + 200, "adds sharing", "g") + tag(ox, y0 + 230, "aliasing, dangling pointers", "p"))
    # general graph
    ox = 470
    o.append(T(ox, y0 + 30, "General graph", "h") + dnode(ox + 150, y0 + 66, "root"))
    o.append(edge(ox + 150, y0 + 66, ox + 70, y0 + 112) + dnode(ox + 70, y0 + 112, "avi"))
    o.append(edge(ox + 150, y0 + 66, ox + 230, y0 + 112) + dnode(ox + 230, y0 + 112, "text"))
    o.append(edge(ox + 230, y0 + 112, ox + 230, y0 + 164) + dnode(ox + 230, y0 + 164, "book"))
    o.append(P(f"M{ox + 266},{y0 + 164} C{ox + 350},{y0 + 164} {ox + 340},{y0 + 66} {ox + 188},{y0 + 62}", "p", dash=True))
    o.append(T(ox + 312, y0 + 120, "a link back up", "tp m"))
    o.append(tag(ox, y0 + 200, "cycles possible", "p") + tag(ox, y0 + 230, "fix: garbage collection, cycle detection", "n"))
    return fig(512, "".join(o), "Each structure fixes the problem of the one before it: naming, then grouping, then sharing; a general graph allows cycles.",
               "Single-level, two-level, tree, acyclic-graph and general-graph directories")


# ------------------------------------------------------------------ 5 · protection: chmod 761
def f_chmod():
    o = [T(20, 30, "chmod 761 game", "h mono")]
    labels = [(150, "bits"), (194, "weights"), (228, "number"), (262, "letters")]
    o += [T(20, y, s, "m") for y, s in labels]
    for gx, name, bits, sumtxt, letters in ((150, "owner", "111", "4 + 2 + 1 = 7", "rwx"),
                                            (380, "group", "110", "4 + 2 = 6", "rw-"),
                                            (610, "public", "001", "1", "--x")):
        o.append(T(gx + 90, 72, name, "h", "middle"))
        for i, (b, l, wgt) in enumerate(zip(bits, "rwx", "421")):
            x = gx + i * 62
            o.append(T(x + 28, 100, l, "m mono", "middle"))
            o.append(R(x, 110, 56, 56, "c-g" if b == "1" else "c-n") + T(x + 28, 146, b, "big " + ("tg" if b == "1" else "m"), "middle"))
            o.append(T(x + 28, 194, wgt, "m mono", "middle"))
        o.append(T(gx + 90, 228, sumtxt, "h mono", "middle"))
        o.append(T(gx + 90, 262, letters, "tg big mono", "middle"))
    return fig(282, "".join(o), "Each class gets three bits, r w x, worth 4, 2 and 1. Add the bits that are on: 7, 6, 1.",
               "chmod 761: owner rwx is 7, group rw- is 6, public --x is 1")


# ------------------------------------------------------------------ 6 · layered file system
def f_layers():
    rows = [("Application programs", "the programs that use files", "c-n"),
            ("Logical file system", "metadata, FCBs, directories, protection", "c-n"),
            ("File-organization module ★", "logical to physical blocks, free space", "c-y"),
            ("Basic file system", "“retrieve block 123”, buffers and caches", "c-n"),
            ("I/O control", "device drivers, low-level hardware commands", "c-n"),
            ("Devices", "the disk", "c-n")]
    o = [T(62, 26, "highest", "m", "middle")]
    for i, (n, d, c) in enumerate(rows):
        y = 40 + i * 58
        o.append(R(120, y, 720, 46, c) + T(140, y + 29, n, "h" + (" ty" if c == "c-y" else "")) + T(450, y + 29, d, "m"))
    o.append(L(62, 40, 62, 380, "n"))
    o.append(T(62, 404, "lowest", "m", "middle"))
    o.append(T(120, 404, "Layering: less complexity and redundancy, but more overhead.", "m"))
    return fig(418, "".join(o), "A request goes down the stack: name to FCB, logical to physical block, block command, device driver, disk.",
               "File-system layers from application programs down to devices")


# ------------------------------------------------------------------ 7 · implementation structures
def f_impl():
    o = [T(20, 30, "ON DISK", "h mono"), T(450, 30, "IN MEMORY", "h mono")]
    left = [("Boot control block", "info to boot the OS; the first block"),
            ("Volume control block", "superblock in UNIX; master file table in NTFS"),
            ("Directory structure", "file names and inode numbers"),
            ("FCB (inode), one per file", "permissions, size, data-block pointers")]
    for i, (a, b) in enumerate(left):
        o.append(box(20, 46 + i * 60, 340, 50, a, b, cls="c-y" if i == 3 else "c-n", tcls="h" + (" ty" if i == 3 else ""), a="start"))
    o.append(box(450, 46, 390, 50, "Mount table", "mounts, mount points, file-system types", a="start"))
    o.append(box(450, 106, 390, 50, "Directory-structure cache", "recently used directories", a="start"))
    o.append(R(450, 168, 390, 66, "c-g") + T(464, 192, "System-wide open-file table", "h tg")
             + T(464, 212, "a copy of each open file's FCB", "m") + T(464, 228, "open count = 2", "tg mono"))
    o.append(box(450, 290, 186, 54, "Process A", "per-process table", cls="c-b", tcls="h tb"))
    o.append(box(654, 290, 186, 54, "Process B", "per-process table", cls="c-b", tcls="h tb"))
    o.append(L(543, 288, 590, 238, "g") + L(747, 288, 700, 238, "g"))
    o.append(T(645, 272, "both point here", "tg sm", "middle"))
    o.append(box(450, 362, 390, 44, "Buffers", "", a="start"))
    o.append(T(600, 389, "blocks in transit", "m"))
    o.append(P("M362,272 C410,272 410,200 446,200", "y", dash=True))
    o.append(T(20, 316, "open copies the FCB into memory", "ty m"))
    o.append(T(20, 338, "close writes the entry back to disk", "m"))
    return fig(420, "".join(o), "Open copies the FCB into the system-wide table once; each process that opens the file gets its own entry pointing there.",
               "On-disk and in-memory file-system structures, with two processes sharing one open-file entry")


# ------------------------------------------------------------------ 8 · allocation methods
def grid(px, py, cells, size=32):
    o = []
    for b in range(32):
        x, y = px + (b % 8) * size, py + (b // 8) * size
        cls, tc = cells.get(b, ("c-n", "m"))
        o.append(R(x + 1, y + 1, size - 2, size - 2, cls, 5) + T(x + size / 2, y + size / 2 + 4, str(b), f"mono sm {tc}", "middle"))
    return "".join(o)


def cc(px, py, b, size=32):
    return px + (b % 8) * size + size / 2, py + (b // 8) * size + size / 2


def strip(px, y, items, cls, tc, size=36, gap=6, arrows=False, c="g"):
    o = []
    for i, it in enumerate(items):
        x = px + i * (size + gap)
        k, t = (("c-p", "tp") if it in ("nil", "end") else (cls, tc))
        o.append(R(x, y, size, 28, k, 5) + T(x + size / 2, y + 19, it, f"mono sm {t}", "middle"))
        if arrows and i < len(items) - 1:
            o.append(L(x + size + 1, y + 14, x + size + gap - 1, y + 14, c))
    return "".join(o)


def f_alloc():
    o, py = [], 48
    chain = [9, 16, 1, 10, 25]
    # contiguous
    px = 20
    o.append(T(px, 30, "Contiguous", "h") + grid(px, py, {b: ("c-y", "ty") for b in range(19, 25)}))
    o.append(T(px, 202, "one run of blocks", "m sm") + strip(px, 210, [str(b) for b in range(19, 25)], "c-y", "ty", gap=2))
    o.append(R(px, 252, 256, 34, "c-n") + T(px + 14, 274, "mail · start 19 · length 6", "mono"))
    o.append(tag(px, 300, "fast sequential and random", "g") + tag(px, 330, "external fragmentation", "p"))
    # linked
    px = 302
    o.append(T(px, 30, "Linked", "h") + grid(px, py, {b: ("c-g", "tg") for b in chain}))
    o.append(T(px, 202, "each block points to the next", "m sm") + strip(px, 210, [str(b) for b in chain] + ["nil"], "c-g", "tg", size=34, gap=10, arrows=True))
    o.append(R(px, 252, 256, 34, "c-n") + T(px + 14, 274, "jeep · start 9 · end 25", "mono"))
    o.append(tag(px, 300, "no external fragmentation", "g") + tag(px, 330, "slow direct access", "p"))
    # indexed
    px = 584
    cells = {b: ("c-g", "tg") for b in chain}
    cells[19] = ("c-b", "tb")
    o.append(T(px, 30, "Indexed", "h") + grid(px, py, cells))
    o.append(T(px, 202, "index block 19 holds the pointers", "tb sm") + strip(px, 210, [str(b) for b in chain] + ["−1"], "c-b", "tb", gap=8))
    o.append(R(px, 252, 256, 34, "c-n") + T(px + 14, 274, "jeep · index block 19", "mono"))
    o.append(tag(px, 300, "random, no ext. fragmentation", "g") + tag(px, 330, "index block overhead", "p"))
    return fig(362, "".join(o), "The same disk three ways: mail in one run of blocks; jeep as a chain ending at nil; jeep again with index block 19 holding pointers to all its blocks.",
               "Contiguous, linked and indexed allocation on a 32-block disk")


def f_fat_index():
    o = [T(20, 28, "FAT: the jeep chain kept in a table", "h")]
    o.append(R(20, 44, 150, 32, "c-n") + T(34, 65, "jeep · start 9", "mono"))
    rows = [1, 9, 10, 16, 25]
    nxt = {1: "10", 9: "16", 10: "25", 16: "1", 25: "end"}
    tx, ty0 = 120, 112
    o.append(T(tx + 30, ty0 - 10, "block", "m sm", "middle") + T(tx + 110, ty0 - 10, "next", "m sm", "middle"))
    ry = {}
    for i, b in enumerate(rows):
        y = ty0 + i * 34
        ry[b] = y + 15
        o.append(R(tx, y, 160, 30, "c-g" if b != 25 else "c-g", 5) + T(tx + 30, y + 20, str(b), "mono tg", "middle")
                 + L(tx + 62, y + 4, tx + 62, y + 26, "n", arrow=False, extra="soft")
                 + T(tx + 110, y + 20, nxt[b], "mono " + ("tp" if b == 25 else "tg"), "middle"))
    o.append(P(f"M95,76 Q95,{ry[9]} {tx - 4},{ry[9]}", "y"))
    for (a, b), side, off in (((9, 16), "r", 34), ((16, 1), "l", 30), ((1, 10), "r", 64), ((10, 25), "l", 56)):
        if side == "r":
            x = tx + 160
            o.append(P(f"M{x},{ry[a]} C{x + off},{ry[a]} {x + off},{ry[b]} {x + 4},{ry[b]}", "g"))
        else:
            o.append(P(f"M{tx},{ry[a]} C{tx - off},{ry[a]} {tx - off},{ry[b]} {tx - 4},{ry[b]}", "g"))
    o.append(T(20, 304, "Same chain as linked allocation, but in one table that can be cached.", "m"))
    # two-level index
    ox = 470
    o.append(T(ox, 28, "Two-level index", "h"))
    o.append(box(ox, 120, 104, 60, "outer index", cls="c-b", tcls="h tb"))
    o.append(box(ox + 170, 60, 110, 46, "index block", cls="c-b", tcls="tb"))
    o.append(box(ox + 170, 194, 110, 46, "index block", cls="c-b", tcls="tb"))
    o.append(L(ox + 106, 140, ox + 166, 88, "b") + L(ox + 106, 162, ox + 166, 214, "b"))
    for i, y in enumerate((40, 80, 176, 216)):
        o.append(R(ox + 330, y, 60, 28, "c-g", 5) + T(ox + 360, y + 19, "data", "tg sm", "middle"))
        sy = 83 if i < 2 else 217
        o.append(L(ox + 282, sy, ox + 326, y + 14, "g", extra="soft"))
    o.append(T(ox, 282, "Outer index, then index block, then data block:", "m"))
    o.append(T(ox, 304, "up to 2 index reads before the data.", "m"))
    return fig(320, "".join(o), "FAT follows the chain inside a table instead of inside each block. A two-level index adds an outer index above the index blocks.",
               "FAT table for the jeep chain, and a two-level index")


def f_mapping():
    x0, w = 40, 120
    o = [T(x0, 24, "Where does logical address 3000 fall? Blocks of 512 units.", "h")]
    for i in range(6):
        x = x0 + i * w
        o.append(T(x + w / 2, 62, f"Q = {i}", "m mono", "middle"))
        o.append(R(x + 2, 72, w - 4, 42, "c-y" if i == 5 else "c-n", 6)
                 + T(x + w / 2, 98, f"{i * 512}–{i * 512 + 511}", "mono sm " + ("ty" if i == 5 else "m"), "middle"))
    mx = x0 + 3000 / 512 * w
    o.append(L(mx, 50, mx, 120, "p", arrow=False) + T(mx, 44, "3000", "tp mono h", "middle"))
    o.append(P(f"M{x0 + 5 * w + 2},126 v8 H{mx} v-8", "b", arrow=False) + T((x0 + 5 * w + mx) / 2, 154, "R = 440", "tb mono", "middle"))
    o.append(T(x0, 192, "3000 ÷ 512 = 5, remainder 440. Q = 5 blocks from the start: block 19 + 5 = 24, displacement 440.", "h"))
    return fig(210, "".join(o), "Q counts whole blocks from the start of the file; R is the position inside the block.",
               "Logical address 3000 falls in the sixth block, Q 5, with remainder 440")


# ------------------------------------------------------------------ 9 · free space
def f_free():
    o = [T(20, 26, "Bit vector: blocks 0, 1, 5, 9 and 15 free", "h")]
    bits, x0 = "1100010001000001", 62
    for i, b in enumerate(bits):
        x = x0 + i * 46
        o.append(R(x, 40, 42, 42, "c-g" if b == "1" else "c-n", 6) + T(x + 21, 67, b, "mono h " + ("tg" if b == "1" else "m"), "middle"))
        o.append(T(x + 21, 102, str(i), "mono sm m", "middle"))
    o.append(T(20, 130, "1 = free, 0 = occupied.", "m"))
    o.append(T(20, 172, "First free block in 8-bit words", "h"))
    words = ["00000000", "00000000", "00101000"]
    for k, wd in enumerate(words):
        wx = 62 + k * 216
        for i, b in enumerate(wd):
            first = k == 2 and i == 2
            cls = "c-y" if first else ("c-g" if b == "1" else "c-n")
            o.append(R(wx + i * 24, 186, 22, 30, cls, 4) + T(wx + i * 24 + 11, 206, b, "mono sm " + ("ty" if first else "tg" if b == "1" else "m"), "middle"))
        o.append(T(wx + 96, 236, ["word 0: all 0", "word 1: all 0", "first 1 at offset 2"][k], "m sm", "middle"))
    o.append(T(720, 200, "8 × 2 + 2 = 18", "h mono") + T(720, 222, "block 18", "ty"))
    o.append(L(20, 258, 840, 258, "n", arrow=False, dash=True, extra="soft"))
    o.append(T(20, 288, "Linked free list", "h"))
    o.append(box(20, 304, 64, 36, "head"))
    xs = [120, 200, 280, 360]
    o.append(L(86, 322, xs[0] - 4, 322, "g"))
    for i, b in enumerate((2, 3, 4, 5)):
        o.append(box(xs[i], 304, 56, 36, str(b), cls="c-g", tcls="mono tg"))
        if i < 3:
            o.append(L(xs[i] + 58, 322, xs[i + 1] - 4, 322, "g"))
    o.append(L(418, 322, 436, 322, "g", arrow=False, dash=True))
    o.append(T(20, 364, "Each free block points to the next.", "m"))
    o.append(T(470, 288, "Grouping", "h"))
    for i, s in enumerate(("3", "4", "5", "8", "next")):
        cls, tc = ("c-b", "tb") if s == "next" else ("c-g", "tg")
        o.append(R(470 + i * 52, 304, 50, 36, cls, 5) + T(495 + i * 52, 327, s, f"mono {tc}", "middle"))
    o.append(L(730, 322, 762, 322, "b") + box(766, 304, 74, 36, "group", cls="c-n", tcls="m"))
    o.append(T(470, 364, "Block 2 stores the next n−1 free addresses, then a pointer.", "m"))
    o.append(L(20, 386, 840, 386, "n", arrow=False, dash=True, extra="soft"))
    o.append(T(20, 414, "Counting: (first free block, count)", "h"))
    free = {2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 17, 18, 25, 26, 27}
    sx = 38
    for b in range(28):
        o.append(R(sx + b * 28 + 1, 428, 26, 32, "c-g" if b in free else "c-n", 4) + T(sx + b * 28 + 14, 449, str(b), "mono sm " + ("tg" if b in free else "m"), "middle"))
    for first, n in ((2, 4), (8, 6), (17, 2), (25, 3)):
        a, b = sx + first * 28 + 2, sx + (first + n) * 28 - 2
        o.append(P(f"M{a},466 v8 H{b} v-8", "g", arrow=False) + T((a + b) / 2, 494, f"({first}, {n})", "tg mono", "middle"))
    return fig(510, "".join(o), "Four ways to remember free blocks: one bit each, a chain, groups of addresses, or runs written as (first, count).",
               "Bit vector, first-free-block search, linked free list, grouping and counting")


TOPIC = {"1": [f_locks()], "2": [f_access()], "3": [f_disks()], "4": [f_dirs()], "5": [f_chmod()],
         "6": [f_layers()], "7": [f_impl()], "8": [f_alloc(), f_fat_index()], "9": [f_free()]}
CALC = {"8": [f_mapping()]}
