#!/usr/bin/env python3
"""Generates the SVG drawing sheets used by the profile README.

GitHub strips CSS, fonts and scripts from READMEs, so every designed piece of the
page is an SVG image instead. The concept is an engineering drawing set: sheet 01
is the high-level design of the whole system, sheets 02-04 detail each part, and
sheet 05 is the bill of materials and revision history. Edit the copy below and run:

    python3 assets/build.py
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent

BG = "#0f2d4a"
LINE, MUTED, SOFT = "#e6eefa", "#8eaacb", "#c3d4ea"
AMBER, RED = "#ffb547", "#ff6b5b"

DIN = "'DIN Alternate', 'DIN Condensed', Bahnschrift, 'D-DIN', 'Barlow Semi Condensed', 'Roboto Condensed', 'Arial Narrow', Arial, sans-serif"
MONO = "'SF Mono', SFMono-Regular, ui-monospace, Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "'Helvetica Neue', Helvetica, 'Segoe UI', Arial, sans-serif"

SHEETS = 5

DEFS = f"""
<pattern id="minor" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#fff" stroke-opacity=".045"/></pattern>
<pattern id="major" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M100 0H0V100" fill="none" stroke="#fff" stroke-opacity=".09"/></pattern>
<pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="{LINE}" stroke-opacity=".3" stroke-width="1.5"/></pattern>
<radialGradient id="vignette" cx=".5" cy=".4" r=".8"><stop offset="0" stop-color="#1a4a78" stop-opacity=".5"/><stop offset="1" stop-color="#05121f" stop-opacity=".55"/></radialGradient>
<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L10 5 L0 9 Z" fill="{LINE}"/></marker>
<marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L10 5 L0 9 Z" fill="{RED}"/></marker>
<marker id="arrow-amber" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L10 5 L0 9 Z" fill="{AMBER}"/></marker>
"""

CSS = f"""
.din {{ font-family: {DIN}; font-weight: 700; }}
.mono {{ font-family: {MONO}; }}
.sans {{ font-family: {SANS}; }}
.flow {{ stroke-dasharray: 6 7; animation: flow 1.1s linear infinite; }}
@keyframes flow {{ to {{ stroke-dashoffset: -13; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} .pulse {{ display: none; }} }}
"""

# Rendered widths of DIN headings, measured in Chrome on macOS. They are pinned with
# textLength so fallback fonts (Bahnschrift, Arial) keep the same layout.
WIDTHS = {
    "name": 486.5, "wip0": 298.3, "wip1": 284.3, "wip2": 268.5, "bx-c": 247.4, "bx-a": 255.8,
    "bx-web": 225.4, "bx-b": 151.9, "tb-title": 245.3, "dA": 502.4, "dB": 478.8, "dC": 452.2,
    "a-core": 113.4, "c-core": 81.8, "bom": 239.8, "rev": 131,
}


def mono_w(text, size, ls=0.0):
    return len(text) * (size * 0.602 + ls)


def text(x, y, s, size=14, cls="mono", fill=LINE, anchor=None, ls=None, key=None, extra=""):
    attrs = f'x="{x:g}" y="{y:g}" class="{cls}" font-size="{size}" fill="{fill}"'
    if anchor:
        attrs += f' text-anchor="{anchor}"'
    if ls is not None:
        attrs += f' letter-spacing="{ls}"'
    if key:
        attrs += f' id="{key}"'
        if key in WIDTHS:
            attrs += f' textLength="{WIDTHS[key]}" lengthAdjust="spacingAndGlyphs"'
    return f"<text {attrs}{extra}>{escape(s)}</text>"


def line(x1, y1, x2, y2, stroke=LINE, width=1.5, extra=""):
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{width}"{extra}/>'


def flow(d, stroke=LINE, marker="arrow"):
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="1.6" class="flow" marker-end="url(#{marker})"/>'


def pulse(d, dur, color=AMBER, begin="0s"):
    return (f'<circle class="pulse" r="4.5" fill="{color}"><animateMotion dur="{dur}" begin="{begin}" '
            f'repeatCount="indefinite" path="{d}"/></circle>')


def bubble(cx, cy, letter, r=14, size=14):
    """Detail callout: the circled letter that points to another sheet."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BG}" stroke="{LINE}" stroke-width="1.5"/>'
            + text(cx, cy + size * 0.36, letter, size, "din", anchor="middle"))


def box(x, y, w, h, title, sub=None, ref=None, key=None):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{BG}" stroke="{LINE}" stroke-width="1.6"/>'
    out += text(x + 20, y + (32 if sub else h / 2 + 7), title, 19, "din", key=key)
    if sub:
        out += text(x + 20, y + 56, sub, 12.5, fill=MUTED, ls=0.4)
    if ref:
        out += bubble(x + w, y, ref)
    return out


def node(cx, cy, label, w=120, h=38, stroke=LINE, size=16):
    return (f'<rect x="{cx - w / 2:g}" y="{cy - h / 2:g}" width="{w}" height="{h}" fill="{BG}" stroke="{stroke}" stroke-width="1.5"/>'
            + text(cx, cy + size * 0.36, label, size, "din", anchor="middle", fill=stroke))


def diamond(cx, cy, r=20, stroke=RED):
    return (f'<path d="M{cx} {cy - r} L{cx + r} {cy} L{cx} {cy + r} L{cx - r} {cy} Z" fill="{BG}" stroke="{stroke}" stroke-width="2"/>'
            + text(cx, cy + 5, "?", 14, "din", anchor="middle", fill=stroke))


def frame(w, h, zones=True):
    """Sheet border with the lettered and numbered zone bands of a drawing."""
    o, i = 12, 32
    out = [
        f'<rect x="{o}" y="{o}" width="{w - 2 * o}" height="{h - 2 * o}" fill="none" stroke="{LINE}" stroke-width="2"/>',
        f'<rect x="{i}" y="{i}" width="{w - 2 * i}" height="{h - 2 * i}" fill="none" stroke="{LINE}" stroke-width="1" stroke-opacity=".8"/>',
    ]
    if not zones:
        return "".join(out)
    cols, rows = 6, max(2, round(h / 200))
    cw, rh = (w - 2 * i) / cols, (h - 2 * i) / rows
    for c in range(cols):
        cx = i + cw * (c + 0.5)
        for y in (o + 14, h - o - 6):
            out.append(text(cx, y, str(c + 1), 10, fill=MUTED, anchor="middle"))
        if c:
            x = i + cw * c
            out += [line(x, o, x, i, MUTED, 1), line(x, h - i, x, h - o, MUTED, 1)]
    for r in range(rows):
        cy = i + rh * (r + 0.5) + 4
        for x in (o + 10, w - o - 10):
            out.append(text(x, cy, "ABCDEFGH"[r], 10, fill=MUTED, anchor="middle"))
        if r:
            y = i + rh * r
            out += [line(o, y, i, y, MUTED, 1), line(w - i, y, w - o, y, MUTED, 1)]
    return "".join(out)


def sheet(w, h, body, title, zones=True):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<title>{escape(title)}</title>
<defs>{DEFS}<clipPath id="clip"><rect width="{w}" height="{h}" rx="14"/></clipPath></defs>
<style>{CSS}</style>
<g clip-path="url(#clip)">
<rect width="{w}" height="{h}" fill="{BG}"/>
<rect width="{w}" height="{h}" fill="url(#minor)"/>
<rect width="{w}" height="{h}" fill="url(#major)"/>
<rect width="{w}" height="{h}" fill="url(#vignette)"/>
{frame(w, h, zones)}
{body}
</g>
</svg>
"""


# ---------------------------------------------------------------- sheet 01: high-level design

WIP = [
    ("A", "WEB BROWSER AUTOMATION AGENT", "chromeboost.work", "IN SERVICE"),
    ("B", "AI INFERENCE COST OPTIMISATION", "cost per task ↓, quality held", "IN DEVELOPMENT"),
    ("C", "PERSONAL ASSISTANT AI AGENT", "inbox · calendar · follow-ups", "IN DEVELOPMENT"),
]


def status(x, y, s, size=12, anchor=None):
    live = s == "IN SERVICE"
    return text(x, y, ("● " if live else "○ ") + s, size, fill=AMBER if live else SOFT, ls=1.4, anchor=anchor)


def hero():
    W, H = 1200, 740
    b = [
        text(60, 72, "HLD-001  ·  HIGH-LEVEL DESIGN", 12, fill=MUTED, ls=2.4, extra=' xml:space="preserve"'),
        text(1140, 72, "GITHUB.COM/LORDAMDAL", 12, fill=MUTED, ls=2.4, anchor="end"),
    ]

    # The name, dimensioned like a part on a drawing
    name_w = WIDTHS.get("name", 520)
    x0, x1, dy = 62, 62 + name_w, 106
    label = "AI ENGINEER"
    gap = mono_w(label, 13, 2.4) / 2 + 14
    mid = (x0 + x1) / 2
    b += [
        line(x0, 94, x0, 118, MUTED, 1), line(x1, 94, x1, 118, MUTED, 1),
        f'<path d="M{mid - gap:g} {dy} H{x0 + 1}" stroke="{LINE}" stroke-width="1.2" marker-end="url(#arrow)"/>',
        f'<path d="M{mid + gap:g} {dy} H{x1 - 1}" stroke="{LINE}" stroke-width="1.2" marker-end="url(#arrow)"/>',
        text(mid, dy + 4.5, label, 13, fill=LINE, ls=2.4, anchor="middle"),
        text(58, 202, "AHMED ALI", 100, "din", key="name"),
        text(62, 242, "AGENT SYSTEMS  ·  INFERENCE ECONOMICS", 15, fill=AMBER, ls=3, extra=' xml:space="preserve"'),
    ]
    for j, s in enumerate([
        "I design and build AI agents that do real work in the",
        "real world — in your browser, across your week — and the",
        "inference layer that makes them cheap enough to leave on.",
    ]):
        b.append(text(62, 286 + j * 28, s, 20, "sans", fill=SOFT))

    # Work-in-progress schedule
    b += [
        text(72, 390, "REF", 11, fill=MUTED, ls=1.6), text(124, 390, "WORK IN PROGRESS", 11, fill=MUTED, ls=1.6),
        text(456, 390, "STATUS", 11, fill=MUTED, ls=1.6), line(60, 400, 600, 400, LINE, 1.2),
    ]
    for r, (ref, item, sub, st) in enumerate(WIP):
        y = 400 + r * 52
        b += [
            bubble(90, y + 26, ref, r=13, size=13),
            text(124, y + 25, item, 19, "din", key=f"wip{r}"),
            text(124, y + 43, sub, 12, fill=MUTED, ls=0.3),
            status(456, y + 31, st),
            line(60, y + 52, 600, y + 52, LINE, 1, ' stroke-opacity=".35"'),
        ]

    # Fig. 1: the system
    b += [
        f'<circle cx="706" cy="150" r="34" fill="{BG}" stroke="{LINE}" stroke-width="1.6"/>',
        text(706, 157, "YOU", 18, "din", anchor="middle"),
        box(820, 112, 320, 76, "PERSONAL ASSISTANT AGENT", "plans · remembers · schedules", "C", "bx-c"),
        box(820, 248, 320, 76, "BROWSER AUTOMATION AGENT", "observe · act · verify", "A", "bx-a"),
        f'<rect x="820" y="420" width="320" height="50" fill="{BG}" stroke="{LINE}" stroke-width="1.6"/>',
        '<rect x="820" y="420" width="320" height="50" fill="url(#hatch)"/>',
        f'<rect x="840" y="432" width="280" height="26" fill="{BG}"/>',
        text(980, 451, "THE WEB · YOUR OWN CHROME", 17, "din", anchor="middle", key="bx-web"),
        f'<rect x="650" y="500" width="490" height="56" fill="{BG}" stroke="{LINE}" stroke-width="1.6"/>',
        f'<rect x="654" y="504" width="482" height="48" fill="none" stroke="{LINE}" stroke-width=".8" stroke-opacity=".5"/>',
        text(800, 527, "INFERENCE LAYER", 19, "din", key="bx-b"),
        text(800, 545, "cost per task ↓ · quality held fixed", 12.5, fill=MUTED, ls=0.4),
        bubble(1140, 500, "B"),
        diamond(980, 372),
        text(1012, 377, "you approve", 12.5, fill=RED, ls=0.4),
        flow("M740 150 H818"), text(779, 140, "intent", 12, fill=MUTED, anchor="middle"),
        flow("M980 188 V246"), text(992, 222, "web tasks", 12, fill=MUTED),
        flow("M980 324 V349"), flow("M980 393 V418"),
        flow("M780 500 V174 H818"), flow("M780 300 H818"),
        text(770, 420, "model calls", 12, fill=MUTED, anchor="middle", extra=' transform="rotate(-90 770 420)"'),
        pulse("M740 150 H818 M980 188 V246 M980 324 V349 M980 393 V418", "3.2s"),
        pulse("M780 500 V174 H818", "2.6s", begin="1.2s"),
        text(650, 582, "FIG. 1 — ONE SYSTEM, THREE PARTS", 11, fill=MUTED, ls=1.6),
    ]

    # Legend
    b += [
        f'<rect x="60" y="596" width="410" height="92" fill="{BG}" fill-opacity=".6" stroke="{LINE}" stroke-width="1" stroke-opacity=".6"/>',
        text(74, 616, "LEGEND", 11, fill=MUTED, ls=1.6),
        line(74, 641, 112, 641, LINE, 1.6), text(124, 646, "component", 13, fill=SOFT),
        f'<path d="M74 669 H112" stroke="{LINE}" stroke-width="1.6" class="flow"/>', text(124, 674, "intent / data flow", 13, fill=SOFT),
        f'<path d="M292 629 L304 641 L292 653 L280 641 Z" fill="none" stroke="{RED}" stroke-width="1.8"/>', text(316, 646, "human approval", 13, fill=SOFT),
        f'<rect x="280" y="661" width="24" height="16" fill="url(#hatch)" stroke="{LINE}" stroke-width="1"/>', text(316, 674, "external system", 13, fill=SOFT),
    ]

    # Title block
    cells = [
        (690, 590, 330, 50, "TITLE", "AGENTS THAT DO REAL WORK", "din", 19),
        (1020, 590, 148, 50, "SHEET", f"01 / {SHEETS:02d}", "din", 19),
        (690, 640, 110, 68, "DRAWN", "A. ALI", "mono", 15),
        (800, 640, 220, 68, "CONTACT", "me@lordamdal.com", "mono", 15),
        (1020, 640, 70, 68, "REV", "C", "din", 19),
        (1090, 640, 78, 68, "YEAR", "2026", "mono", 15),
    ]
    b.append(f'<rect x="690" y="590" width="478" height="118" fill="{BG}" stroke="{LINE}" stroke-width="1.6"/>')
    for x, y, w, h, lab, val, cls, size in cells:
        b += [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{LINE}" stroke-width="1"/>',
            text(x + 12, y + 16, lab, 10, fill=MUTED, ls=1.5),
            text(x + 12, y + h - 13, val, size, cls, key="tb-title" if lab == "TITLE" else None),
        ]
    return sheet(W, H, "\n".join(b), "Ahmed Ali, AI engineer. High-level design: you, a personal assistant agent, a browser automation agent and the web, all running on a cost-optimised inference layer")


# ---------------------------------------------------------------- sheets 02-04: details

def detail(ref, n, title, st, notes, drawing):
    W, H = 1200, 440
    b = [
        bubble(88, 94, ref, r=22, size=22),
        text(126, 80, f"DETAIL {ref}  ·  SHEET {n:02d} / {SHEETS:02d}", 12, fill=MUTED, ls=2.2, extra=' xml:space="preserve"'),
        text(124, 114, title, 32, "din", key=f"d{ref}"),
        status(1140, 100, st, 13, anchor="end"),
        line(60, 134, 1140, 134, LINE, 1, ' stroke-opacity=".5"'),
        line(630, 160, 630, 392, LINE, 1, ' stroke-opacity=".25" stroke-dasharray="2 5"'),
        text(660, 180, "NOTES", 11, fill=MUTED, ls=1.6),
    ]
    for j, s in enumerate(notes):
        y = 214 + j * 34
        b += [text(660, y, f"{j + 1}.", 15, fill=AMBER), text(690, y, s, 15, fill=LINE)]
    b.append(drawing)
    return sheet(W, H, "\n".join(b), f"Detail {ref}: {title.title()}. " + " ".join(notes))


def ellipse_pt(cx, cy, rx, ry, deg):
    a = math.radians(deg)
    return cx + rx * math.cos(a), cy + ry * math.sin(a)


def drawing_a():
    cx, cy, rx, ry = 330, 282, 200, 86
    steps = [(180, "OBSERVE"), (270, "PLAN"), (360, "ACT"), (450, "VERIFY")]
    out = []
    for k, (deg, _) in enumerate(steps):
        nxt = steps[(k + 1) % 4][0] + (360 if k == 3 else 0)
        pad = lambda d: 18 if d % 180 == 0 else 22
        (x0, y0), (x1, y1) = ellipse_pt(cx, cy, rx, ry, deg + pad(deg)), ellipse_pt(cx, cy, rx, ry, nxt - pad(nxt))
        out.append(flow(f"M{x0:.1f} {y0:.1f} A{rx} {ry} 0 0 1 {x1:.1f} {y1:.1f}"))
    for deg, label in steps:
        x, y = ellipse_pt(cx, cy, rx, ry, deg)
        out.append(node(x, y, label))
    out += [
        text(cx, cy - 4, "YOUR CHROME", 18, "din", anchor="middle", key="a-core"),
        text(cx, cy + 18, "your logins · your profile", 12, fill=MUTED, anchor="middle"),
        pulse(f"M{cx - rx} {cy} A{rx} {ry} 0 1 1 {cx + rx} {cy} A{rx} {ry} 0 1 1 {cx - rx} {cy}", "7s"),
        flow(f"M{cx + rx} {cy + 19} V{cy + 62}", RED, "arrow-red"),
        diamond(cx + rx, cy + 84),
        text(cx + rx + 10, cy + 45, "irreversible", 12, fill=RED),
        text(cx + rx + 28, cy + 89, "you click", 12, fill=RED),
    ]
    return "".join(out)


def bezier_y_at(p, x):
    """y on a cubic bezier (control points p) at a given x, by bisection on t."""
    weights = lambda t: ((1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3)
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2
        lo, hi = (t, hi) if sum(c[0] * w for c, w in zip(p, weights(t))) < x else (lo, t)
    return sum(c[1] * w for c, w in zip(p, weights((lo + hi) / 2)))


def drawing_b():
    ox, oy, top, right = 110, 368, 160, 584
    today = [(140, 346), (300, 336), (430, 296), (540, 172)]
    target = [(140, 356), (320, 351), (450, 331), (540, 268)]
    px = 470
    y0, y1 = bezier_y_at(today, px), bezier_y_at(target, px)
    curve = lambda p: "M{} {} C{} {} {} {} {} {}".format(*[v for pt in p for v in pt])
    return "".join([
        f'<path d="M{ox} {oy} V{top}" stroke="{LINE}" stroke-width="1.6" marker-end="url(#arrow)"/>',
        f'<path d="M{ox} {oy} H{right}" stroke="{LINE}" stroke-width="1.6" marker-end="url(#arrow)"/>',
        text(ox + 12, top + 8, "COST / TASK", 12, fill=MUTED, ls=1.4),
        text(right, oy - 12, "QUALITY", 12, fill=MUTED, ls=1.4, anchor="end"),
        f'<path d="{curve(today)}" fill="none" stroke="{LINE}" stroke-width="2"/>',
        text(550, 176, "today", 12.5, fill=SOFT),
        f'<path d="{curve(target)}" fill="none" stroke="{AMBER}" stroke-width="2" class="flow"/>',
        text(550, 272, "target", 12.5, fill=AMBER),
        line(px, y0, px, oy, MUTED, 1, ' stroke-dasharray="3 4"'),
        text(px, oy + 20, "same quality", 12, fill=MUTED, anchor="middle"),
        line(px - 40, y0, px - 8, y0, MUTED, 1), line(px - 40, y1, px - 8, y1, MUTED, 1),
        f'<path d="M{px - 32} {y0 + 1:.1f} V{y1 - 1:.1f}" stroke="{AMBER}" stroke-width="1.4" marker-start="url(#arrow-amber)" marker-end="url(#arrow-amber)"/>',
        text(px - 44, round((y0 + y1) / 2 + 5, 1), "Δ cost", 13, fill=AMBER, anchor="end"),
        f'<circle cx="{px}" cy="{y0:.1f}" r="6" fill="{BG}" stroke="{LINE}" stroke-width="2"/>',
        f'<circle cx="{px}" cy="{y1:.1f}" r="6" fill="{BG}" stroke="{AMBER}" stroke-width="2"/>',
        f'<circle class="pulse" cx="{px}" cy="{y0:.1f}" r="4.5" fill="{AMBER}"><animate attributeName="cy" '
        f'values="{y0:.1f};{y0:.1f};{y1:.1f};{y1:.1f}" keyTimes="0;.3;.7;1" dur="4s" repeatCount="indefinite"/></circle>',
    ])


def drawing_c():
    cx, cy, rx, ry, r = 330, 282, 220, 100, 50
    bw, bh = 128, 34
    spokes = [
        (180, "INBOX", LINE), (-120, "CALENDAR", LINE), (-60, "MEMORY", LINE),
        (0, "FOLLOW-UPS", LINE), (60, "WEB → DETAIL A", LINE), (120, "YOU APPROVE", RED),
    ]
    out = []
    for deg, label, color in spokes:
        x, y = ellipse_pt(cx, cy, rx, ry, deg)
        a = math.radians(deg)
        sx, sy = cx + (r + 4) * math.cos(a), cy + (r + 4) * math.sin(a)
        # stop the spoke just outside the satellite box
        k = min(abs((bw / 2 + 2) / (x - sx)) if abs(x - sx) > 1e-6 else 9,
                abs((bh / 2 + 2) / (y - sy)) if abs(y - sy) > 1e-6 else 9)
        ex, ey = x - (x - sx) * k, y - (y - sy) * k
        out.append(flow(f"M{sx:.1f} {sy:.1f} L{ex:.1f} {ey:.1f}", color, "arrow-red" if color == RED else "arrow"))
    for deg, label, color in spokes:
        x, y = ellipse_pt(cx, cy, rx, ry, deg)
        if label.startswith("WEB"):
            out.append(f'<rect x="{x - bw / 2:g}" y="{y - bh / 2:g}" width="{bw}" height="{bh}" fill="{BG}"/>'
                       f'<rect x="{x - bw / 2:g}" y="{y - bh / 2:g}" width="{bw}" height="{bh}" fill="url(#hatch)" stroke="{LINE}" stroke-width="1.5"/>'
                       f'<rect x="{x - bw / 2 + 6:g}" y="{y - 10:g}" width="{bw - 12}" height="20" fill="{BG}"/>'
                       + text(x, y + 5.4, label, 15, "din", anchor="middle"))
        else:
            out.append(node(x, y, label, w=bw, h=bh, stroke=color, size=15))
    out += [
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BG}" stroke="{LINE}" stroke-width="1.6"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r - 5}" fill="none" stroke="{LINE}" stroke-width=".8" stroke-opacity=".5"/>',
        text(cx, cy + 2, "ASSISTANT", 17, "din", anchor="middle", key="c-core"),
        text(cx, cy + 20, "runs on B", 11, fill=MUTED, anchor="middle"),
    ]
    return "".join(out)


DETAILS = [
    ("A", 2, "WEB BROWSER AUTOMATION AGENT", "IN SERVICE", [
        "Drives your real, logged-in Chrome.",
        "Real input: pointer paths, keystrokes, drag.",
        "Checks what's on top before it clicks.",
        "Posts, payments and deletes wait for your click.",
        "Open source (MIT) · chromeboost.work",
    ], drawing_a),
    ("B", 3, "AI INFERENCE COST OPTIMISATION", "IN DEVELOPMENT", [
        "Measure cost per finished task, not per token.",
        "Find where model spend actually goes first.",
        "Hold quality fixed with evals, then cut cost.",
        "Goal: agents cheap enough to leave running.",
    ], drawing_b),
    ("C", 4, "PERSONAL ASSISTANT AI AGENT", "IN DEVELOPMENT", [
        "Runs the errands of a working week.",
        "Inbox, calendar, and the follow-ups you forget.",
        "Remembers context so you don't repeat yourself.",
        "Hands web work to the browser agent (A).",
        "Runs on the cost-optimised inference layer (B).",
        "Drafts everything; you approve what goes out.",
    ], drawing_c),
]


# ---------------------------------------------------------------- sheet 05: BOM + revisions

BOM = [
    ("Python · PyTorch · TensorFlow", "models, training, pipelines"),
    ("TypeScript · Node.js · React", "agents, extensions, apps"),
    ("MCP · Claude Code", "tool protocols, agent harnesses"),
    ("Swift · Core ML · Flutter", "on-device & mobile"),
    ("Google Cloud ✓ · AWS · Azure", "cloud infrastructure"),
    ("Docker · Kubernetes", "deploy & scale"),
    ("PostgreSQL · MongoDB", "data"),
]

REVISIONS = [
    ("A", ["Deep learning & computer vision"]),
    ("B", ["Real-time video avatars with", "voice agents"]),
    ("C", ["Browser agents, inference cost", "& personal assistants"]),
]


def cloud(x, y, w, h, step=22):
    """Red-pencil revision cloud: scallops traced clockwise around a rectangle."""
    d = [f"M{x} {y}"]
    for (x0, y0), (x1, y1) in [((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)),
                               ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))]:
        length = math.hypot(x1 - x0, y1 - y0)
        n = max(1, round(length / step))
        for k in range(1, n + 1):
            d.append(f"A{length / n / 2:.1f} {length / n / 2:.1f} 0 0 1 {x0 + (x1 - x0) * k / n:.1f} {y0 + (y1 - y0) * k / n:.1f}")
    return f'<path d="{" ".join(d)}" fill="none" stroke="{RED}" stroke-width="1.6" stroke-linejoin="round"/>'


def bom():
    W, H = 1200, 470
    b = [
        text(60, 72, f"SHEET {SHEETS:02d} / {SHEETS:02d}", 12, fill=MUTED, ls=2.2),
        text(60, 112, "BILL OF MATERIALS", 28, "din", key="bom"),
        text(72, 146, "ITEM", 11, fill=MUTED, ls=1.6), text(120, 146, "COMPONENT", 11, fill=MUTED, ls=1.6),
        text(420, 146, "USED FOR", 11, fill=MUTED, ls=1.6), line(60, 156, 700, 156, LINE, 1.2),
        text(770, 112, "REVISIONS", 28, "din", key="rev"),
        text(784, 146, "REV", 11, fill=MUTED, ls=1.6), text(830, 146, "DESCRIPTION", 11, fill=MUTED, ls=1.6),
        line(770, 156, 1140, 156, LINE, 1.2),
    ]
    for r, (part, use) in enumerate(BOM):
        y = 156 + r * 38
        b += [
            text(72, y + 25, f"{r + 1:02d}", 14, fill=MUTED),
            text(120, y + 25, part, 15),
            text(420, y + 25, use, 14, fill=SOFT),
            line(60, y + 38, 700, y + 38, LINE, 1, ' stroke-opacity=".3"'),
        ]
    for r, (rev, desc) in enumerate(REVISIONS):
        y = 156 + r * 74
        color = RED if rev == "C" else LINE
        b.append(f'<path d="M796 {y + 18} L810 {y + 42} L782 {y + 42} Z" fill="none" stroke="{color}" stroke-width="1.5"/>'
                 + text(796, y + 39, rev, 12, "din", anchor="middle", fill=color))
        for j, s in enumerate(desc):
            b.append(text(830, y + 30 + j * 22, s, 14.5, fill=LINE if rev == "C" else SOFT))
        if r < len(REVISIONS) - 1:
            b.append(line(770, y + 74, 1140, y + 74, LINE, 1, ' stroke-opacity=".3"'))
    yc = 156 + 2 * 74
    b += [cloud(774, yc + 6, 362, 64), text(1126, yc + 52, "CURRENT", 11, fill=AMBER, ls=1.6, anchor="end")]
    return sheet(W, H, "\n".join(b), "Bill of materials and revision history")


def end():
    W, H = 1200, 104
    b = [
        text(60, 60, f"END OF DRAWING SET  ·  {SHEETS:02d} SHEETS", 13, fill=MUTED, ls=2.2, extra=' xml:space="preserve"'),
        f'<text x="1140" y="60" class="mono" font-size="15" fill="{LINE}" text-anchor="end" letter-spacing="1.6">'
        f'QUESTIONS <tspan fill="{AMBER}">→</tspan> ME@LORDAMDAL.COM</text>',
    ]
    return sheet(W, H, "\n".join(b), "End of drawing set. Questions: me@lordamdal.com", zones=False)


# ---------------------------------------------------------------- buttons

def button(tag, value):
    """Two-cell tag like a title-block entry: amber key, blueprint value."""
    kw = mono_w(tag, 13, 2) + 26
    vw = mono_w(value, 15, 0.5) + 34
    w, h = kw + vw, 46
    body = (f'<rect x="1" y="1" width="{w:.0f}" height="{h}" fill="{BG}" stroke="{LINE}" stroke-width="1.5"/>'
            f'<rect x="1" y="1" width="{kw:.0f}" height="{h}" fill="{AMBER}" stroke="{LINE}" stroke-width="1.5"/>'
            + text(round(1 + kw / 2 + 1, 1), 29, tag, 13, fill=BG, ls=2, anchor="middle", extra=' font-weight="700"')
            + text(round(1 + kw + vw / 2, 1), 30, value, 15, fill=LINE, ls=0.5, anchor="middle"))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w + 2:.0f}" height="{h + 2}" viewBox="0 0 {w + 2:.0f} {h + 2}" role="img">
<title>{escape(tag)}: {escape(value)}</title>
<style>{CSS}</style>
{body}
</svg>
"""


BUTTONS = {
    "btn-email": ("MAIL", "me@lordamdal.com"),
    "btn-x": ("X", "@theamdal"),
    "btn-linkedin": ("IN", "linkedin/lordamdal"),
    "btn-site": ("WEB", "chromeboost.work"),
    "btn-repo": ("REPO", "lordamdal/chromeboost"),
    "btn-gcp": ("GCP", "cloud skills profile"),
}


def main():
    pages = {"hero": hero(), "bom": bom(), "end": end()}
    for ref, n, title, st, notes, draw in DETAILS:
        pages[f"detail-{ref.lower()}"] = detail(ref, n, title, st, notes, draw())
    pages.update({name: button(*args) for name, args in BUTTONS.items()})
    for name, content in pages.items():
        (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
        print(f"wrote assets/{name}.svg")


if __name__ == "__main__":
    main()
