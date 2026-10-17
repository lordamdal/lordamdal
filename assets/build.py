#!/usr/bin/env python3
"""Generates the SVG panels used by the profile README.

GitHub strips CSS, fonts and scripts from READMEs, so every designed piece of the
page is an SVG image instead. The concept is an open-studio show: gouache and
impasto paint (SVG turbulence + lighting filters) on neo-brutalist boards with
black borders, hard shadows, stickers and tape. Edit the copy below and run:

    python3 assets/build.py
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent

INK, INK_SOFT, CARD, CANVAS = "#141414", "#4a4540", "#fffaf0", "#f7f0e1"
PINK, HOT, RED, ORANGE = "#ff8fb6", "#ff4f8b", "#ff3b1f", "#ff8a1f"
YELLOW, LIME, TEAL, SKY = "#ffd21f", "#b6f03a", "#19c3a6", "#7fd3ff"
COBALT, BLUE, VIOLET, WHITE = "#1f3fd1", "#4d6bff", "#7b5cff", "#fdf6e6"
TAPE = "#f2e6c4"

POSTER = "'Helvetica Neue', 'Arial Narrow', Impact, Haettenschweiler, sans-serif"
SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', SFMono-Regular, ui-monospace, Menlo, Consolas, monospace"

CSS = f"""
.poster {{ font-family: {POSTER}; font-stretch: condensed; font-weight: 900; }}
.sans {{ font-family: {SANS}; }}
.bold {{ font-family: {SANS}; font-weight: 700; }}
.mono {{ font-family: {MONO}; }}
"""

# Rendered widths of poster-type runs, measured in Chrome on macOS. They are pinned
# with textLength so fallback fonts keep the same layout.
WIDTHS = {
    "hero-1": 651.6, "hero-2": 338.6, "hero-hi": 276.1, "k-hero": 123.3, "badge": 72.5, "k-now": 146.6,
    "chip0": 170.2, "chip1": 170.4, "chip2": 210.5, "pal-shadow": 649.6, "pal": 649.6, "k-tools": 190.4,
    "shelf0": 134, "shelf1": 32.3, "shelf2": 49.8, "shelf3": 62.6, "shelf4": 98.8, "shelf5": 79.3,
    "shelf6": 77.3, "dab0": 47, "dab1": 54.1, "dab2": 77.2, "dab3": 71.5, "dab4": 51.4,
    "dab5": 39.4, "dab6": 34.3, "dab7": 57.2, "dab8": 31.9, "dab9": 86.8, "hi": 491.8,
    "w0t0": 359.9, "w0t1": 472, "w1t0": 461.9, "w1t1": 333, "w2t0": 250.3, "w2t1": 425.3,
    "btn-email": 122.1, "btn-x": 178, "btn-linkedin": 94, "btn-site": 244.2, "btn-repo": 296.2, "btn-gcp": 273.9,
}


def filters(w, h, seed=3):
    region = f'filterUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}" color-interpolation-filters="sRGB"'

    def impasto(fid, freq):
        # Thick paint: rough edges from low-frequency noise, bristle ridges from
        # stretched noise, then lit as a height map so the ridges catch light.
        return f"""<filter id="{fid}" {region}>
  <feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="4" seed="{seed}" result="bristle"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="{seed + 6}" result="blob"/>
  <feDisplacementMap in="SourceGraphic" in2="blob" scale="24" xChannelSelector="R" yChannelSelector="G" result="paint"/>
  <feGaussianBlur in="paint" stdDeviation="6" result="soft"/>
  <feColorMatrix in="bristle" type="luminanceToAlpha" result="ridges"/>
  <feComposite in="ridges" in2="paint" operator="in" result="ridgesIn"/>
  <feComposite in="ridgesIn" in2="soft" operator="arithmetic" k2=".75" k3=".65" result="height"/>
  <feDiffuseLighting in="height" surfaceScale="10" diffuseConstant="1.3" lighting-color="#fff" result="diffuse"><feDistantLight azimuth="235" elevation="40"/></feDiffuseLighting>
  <feSpecularLighting in="height" surfaceScale="10" specularConstant=".9" specularExponent="28" lighting-color="#fff" result="spec"><feDistantLight azimuth="235" elevation="40"/></feSpecularLighting>
  <feComposite in="paint" in2="diffuse" operator="arithmetic" k1="1.12" result="lit"/>
  <feComposite in="lit" in2="paint" operator="in" result="litIn"/>
  <feComposite in="spec" in2="paint" operator="in" result="specIn"/>
  <feComposite in="specIn" in2="litIn" operator="arithmetic" k2=".55" k3="1"/>
</filter>"""

    return f"""{impasto("imp", "0.012 0.06")}
{impasto("imp-v", "0.06 0.012")}
<filter id="gouache" {region}>
  <feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="3" seed="{seed + 8}" result="t"/>
  <feDisplacementMap in="SourceGraphic" in2="t" scale="30" xChannelSelector="R" yChannelSelector="G" result="shape"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.05 0.012" numOctaves="3" seed="{seed + 1}" result="streak"/>
  <feColorMatrix in="streak" type="saturate" values="0" result="g"/>
  <feComposite in="shape" in2="g" operator="arithmetic" k2="1" k3=".22" k4="-.11" result="mix"/>
  <feComposite in="mix" in2="shape" operator="in"/>
</filter>
<filter id="torn" x="-5%" y="-30%" width="110%" height="160%">
  <feTurbulence type="fractalNoise" baseFrequency="0.18" numOctaves="2" seed="{seed + 4}" result="t"/>
  <feDisplacementMap in="SourceGraphic" in2="t" scale="7" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{seed + 2}" stitchTiles="stitch"/>
  <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  .22 0 0 0 -.07"/>
</filter>"""


def text(x, y, s, size, cls="sans", fill=INK, anchor=None, ls=None, key=None, extra=""):
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


def stroke(d, color, width):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def text_w(key, fallback):
    return WIDTHS.get(key, fallback)


def sticker(x, y, label, fill, color, key, size=15, ls=1.2, tilt=0.0, h=None, pad=16):
    """Die-cut sticker: white cut line, hard shadow, black border, flat colour."""
    h = h or size + 24
    w = text_w(key, len(label) * (size * 0.68 + ls)) + 2 * pad
    cx, cy = x + w / 2, y + h / 2
    return f"""<g transform="rotate({tilt} {cx:.1f} {cy:.1f})">
<rect x="{x - 6:.1f}" y="{y - 6:.1f}" width="{w + 12:.1f}" height="{h + 12}" rx="10" fill="#fff"/>
<rect x="{x + 5:.1f}" y="{y + 5:.1f}" width="{w:.1f}" height="{h}" rx="6" fill="{INK}"/>
<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="6" fill="{fill}" stroke="{INK}" stroke-width="3.5"/>
{text(x + pad, y + h / 2 + size * 0.36, label, size, "bold", color, ls=ls, key=key)}
</g>""", w


def tape(cx, cy, w=110, angle=-8):
    return (f'<g transform="rotate({angle} {cx} {cy})" filter="url(#torn)">'
            f'<rect x="{cx - w / 2}" y="{cy - 15}" width="{w}" height="30" fill="{TAPE}" fill-opacity=".9"/>'
            f'<rect x="{cx - w / 2}" y="{cy - 15}" width="{w}" height="30" fill="none" stroke="#fff" stroke-opacity=".35" stroke-dasharray="2 9"/>'
            f'</g>')


def board(x, y, w, h, fill=CARD, border=5, shadow=10, rx=4):
    return (f'<rect x="{x + shadow}" y="{y + shadow}" width="{w}" height="{h}" rx="{rx}" fill="{INK}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{INK}" stroke-width="{border}"/>')


def panel(w, h, wall, body, title, seed=3):
    """A wall: flat colour, painted on, black border, hard shadow outside."""
    s = 12
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w + s}" height="{h + s}" viewBox="0 0 {w + s} {h + s}" role="img">
<title>{escape(title)}</title>
<defs>{filters(w, h, seed)}<clipPath id="wall"><rect x="2.5" y="2.5" width="{w - 5}" height="{h - 5}" rx="18"/></clipPath></defs>
<style>{CSS}</style>
<rect x="{s}" y="{s}" width="{w}" height="{h}" rx="20" fill="{INK}"/>
<g clip-path="url(#wall)">
<rect width="{w}" height="{h}" fill="{wall}"/>
{body}
<rect width="{w}" height="{h}" filter="url(#grain)"/>
</g>
<rect x="2.5" y="2.5" width="{w - 5}" height="{h - 5}" rx="18" fill="none" stroke="{INK}" stroke-width="5"/>
</svg>
"""


# ---------------------------------------------------------------- hero

SHOWING = [
    ("01 BROWSER AGENT", COBALT, WHITE),
    ("02 INFERENCE COST", RED, WHITE),
    ("03 PERSONAL ASSISTANT", TEAL, INK),
]


def badge(cx, cy, r, ring, center, fill=YELLOW, tilt=-12):
    """Round sticker with text running around the rim."""
    rr = r - 20
    circ = 2 * math.pi * rr
    return f"""<g transform="rotate({tilt} {cx} {cy})">
<circle cx="{cx}" cy="{cy}" r="{r + 8}" fill="#fff"/>
<circle cx="{cx + 7}" cy="{cy + 7}" r="{r}" fill="{INK}"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="4"/>
<path id="rim" d="M{cx - rr} {cy} a{rr} {rr} 0 1 1 {2 * rr} 0 a{rr} {rr} 0 1 1 {-2 * rr} 0" fill="none"/>
<text class="bold" font-size="14" fill="{INK}" letter-spacing="2"><textPath href="#rim" textLength="{circ - 6:.0f}" lengthAdjust="spacing">{escape(ring)}</textPath></text>
{text(cx, cy + 16, center, 46, "poster", anchor="middle", key="badge")}
</g>"""


def hero():
    W, H = 1200, 720
    gouache = "".join([
        f'<path d="M760 -80 C960 -10 1190 60 1280 280 L1280 -80 Z" fill="{VIOLET}"/>',
        f'<circle cx="1070" cy="660" r="210" fill="{TEAL}"/>',
        f'<circle cx="640" cy="50" r="70" fill="{SKY}"/>',
    ])
    impasto = "".join([
        stroke("M-60 610 C260 530 640 340 1260 150", COBALT, 150),
        stroke("M20 400 C180 372 380 392 600 360", YELLOW, 140),
        stroke("M880 140 C960 90 1050 120 1070 190", RED, 130),
        stroke("M720 660 C800 640 880 668 960 645", WHITE, 50),
        stroke("M690 214 C705 204 720 208 738 218", LIME, 44),
        stroke("M40 676 C120 660 200 684 290 664", HOT, 46),
    ])

    card_x, card_y, card_w, card_h = 784, 250, 366, 300
    body = [
        [("I build AI agents that do", 0)],
        [("real work", 1), (" — in your browser,", 0)],
        [("across your week — and I", 0)],
        [("make them ", 0), ("cheap enough", 1)],
        [("to leave running.", 0)],
    ]
    body_svg = "".join(
        f'<text x="{card_x + 28}" y="{card_y + 106 + i * 32}" class="sans" font-size="22" fill="{INK}">'
        + "".join(f'<tspan font-weight="700">{escape(t)}</tspan>' if b else escape(t) for t, b in line)
        + "</text>"
        for i, line in enumerate(body)
    )
    kicker, _ = sticker(card_x + 18, card_y - 26, "AI ENGINEER", INK, YELLOW, "k-hero", size=15, ls=2.4, tilt=-4)

    chips, x = [], 56
    now, _ = sticker(56, 538, "NOW SHOWING ↓", INK, YELLOW, "k-now", size=14, ls=2.2, tilt=-2)
    for i, (label, fill, color) in enumerate(SHOWING):
        svg, w = sticker(x, 600, label, fill, color, f"chip{i}", size=15, ls=1, tilt=(1.5, -1.5, 1)[i], h=46)
        chips.append(svg)
        x += w + 18

    content = f"""
<g filter="url(#gouache)">{gouache}</g>
<g filter="url(#imp)">{impasto}</g>
{text(52, 252, "AHMED", 220, "poster", key="hero-1")}
{text(52, 462, "ALI.", 220, "poster", key="hero-2")}
<g transform="rotate(2 {card_x + card_w / 2} {card_y + card_h / 2})">
{board(card_x, card_y, card_w, card_h)}
{text(card_x + 28, card_y + 64, "HI, I'M AHMED.", 46, "poster", key="hero-hi")}
{body_svg}
{tape(card_x + card_w - 20, card_y + 6, 100, 38)}
</g>
{kicker}
{badge(1078, 120, 74, "WORKS IN PROGRESS ✶ 2026 ✶ ", "WIP")}
{now}
{"".join(chips)}
"""
    return panel(W, H, PINK, content, "Ahmed Ali — AI engineer. I build AI agents that do real work, and make them cheap enough to leave running.", seed=3)


# ---------------------------------------------------------------- the works

def cursor_points(tx, ty, s):
    pts = [(0, 0), (0, 0.82), (0.2, 0.65), (0.33, 0.97), (0.47, 0.91), (0.34, 0.6), (0.6, 0.6)]
    return " ".join(f"{tx + px * s:.1f},{ty + py * s:.1f}" for px, py in pts)


def burst(cx, cy, r1, r2, n=14):
    pts = []
    for k in range(2 * n):
        a = math.pi * k / n
        r = r1 if k % 2 == 0 else r2
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def art_browser(ox, oy):
    ground = f'<rect x="{ox - 30}" y="{oy - 30}" width="424" height="424" fill="{COBALT}"/>'
    paint = "".join(
        stroke(f"M{ox - 20} {oy + 36 + i * 72} C{ox + 110} {oy + 22 + i * 72} {ox + 240} {oy + 50 + i * 72} {ox + 390} {oy + 30 + i * 72}",
               (BLUE, "#1430a8")[i % 2], 50)
        for i in range(5)
    )
    tip = (ox + 118, oy + 92)
    paint += f'<polygon points="{burst(*tip, 70, 32)}" fill="{RED}"/>'
    paint += (f'<polygon points="{cursor_points(*tip, 220)}" fill="{WHITE}" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>')
    paint += stroke(f"M{ox + 30} {oy + 334} C{ox + 130} {oy + 314} {ox + 250} {oy + 348} {ox + 340} {oy + 322}", YELLOW, 34)
    return f'<g filter="url(#gouache)">{ground}</g><g filter="url(#imp)">{paint}</g>'


def art_inference(ox, oy):
    ground = f'<rect x="{ox - 30}" y="{oy - 30}" width="424" height="424" fill="{YELLOW}"/>'
    bars = "".join(
        stroke(f"M{ox + 62 + i * 80} {oy + 326} V{top}", c, 54)
        for i, (top, c) in enumerate([(oy + 120, RED), (oy + 180, ORANGE), (oy + 240, HOT), (oy + 290, TEAL)])
    )
    (x0, y0), (x1, y1) = (ox + 250, oy + 120), (ox + 330, oy + 236)
    d = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    head = f"{x1 + ux * 26:.1f},{y1 + uy * 26:.1f} {x1 - uy * 22:.1f},{y1 + ux * 22:.1f} {x1 + uy * 22:.1f},{y1 - ux * 22:.1f}"
    arrow = (stroke(f"M{ox + 34} {oy + 46} C{ox + 140} {oy + 50} {x0} {y0} {x1} {y1}", INK, 16)
             + f'<polygon points="{head}" fill="{INK}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    return (f'<g filter="url(#gouache)">{ground}</g><g filter="url(#imp-v)">{bars}</g>'
            f'<g filter="url(#imp)">{arrow}{stroke(f"M{ox + 40} {oy + 346} H{ox + 330}", INK, 10)}</g>')


def art_assistant(ox, oy):
    ground = f'<rect x="{ox - 30}" y="{oy - 30}" width="424" height="424" fill="{VIOLET}"/>'
    bx, by, bw, bh, r = ox + 46, oy + 64, 272, 176, 54
    bubble = (f'<path d="M{bx + r} {by} H{bx + bw - r} A{r} {r} 0 0 1 {bx + bw} {by + r} V{by + bh - r} '
              f'A{r} {r} 0 0 1 {bx + bw - r} {by + bh} H{bx + 120} L{bx + 40} {by + bh + 64} L{bx + 64} {by + bh} '
              f'H{bx + r} A{r} {r} 0 0 1 {bx} {by + bh - r} V{by + r} A{r} {r} 0 0 1 {bx + r} {by} Z" '
              f'fill="{WHITE}" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>')
    dots = "".join(f'<circle cx="{bx + 72 + i * 64}" cy="{by + bh / 2}" r="23" fill="{c}"/>' for i, c in enumerate((RED, YELLOW, TEAL)))
    paint = (stroke(f"M{ox - 20} {oy + 318} C{ox + 90} {oy + 296} {ox + 180} {oy + 330} {ox + 260} {oy + 310}", PINK, 62)
             + bubble + dots + f'<circle cx="{ox + 312}" cy="{oy + 314}" r="36" fill="{YELLOW}" stroke="{INK}" stroke-width="8"/>')
    return f'<g filter="url(#gouache)">{ground}</g><g filter="url(#imp)">{paint}</g>'


WORKS = [
    {
        "n": "01", "wall": YELLOW, "accent": COBALT, "stroke": HOT, "num": WHITE, "side": "left", "art": art_browser,
        "title": ["WEB BROWSER", "AUTOMATION AGENT"],
        "medium": "TypeScript, MCP & your own Chrome",
        "lines": [
            "Claude, driving the Chrome you're already",
            "logged into — real clicks, real typing, and",
            "nothing irreversible without your click.",
        ],
        "status": "ON VIEW — CHROMEBOOST.WORK", "live": True,
    },
    {
        "n": "02", "wall": SKY, "accent": RED, "stroke": YELLOW, "num": WHITE, "side": "right", "art": art_inference,
        "title": ["AI INFERENCE COST", "OPTIMISATION"],
        "medium": "Python, models & a pile of receipts",
        "lines": [
            "Same answers, smaller bill. Measuring cost",
            "per finished task, not per token — and cutting",
            "it without letting quality slip.",
        ],
        "status": "IN THE STUDIO", "live": False,
    },
    {
        "n": "03", "wall": LIME, "accent": VIOLET, "stroke": ORANGE, "num": WHITE, "side": "left", "art": art_assistant,
        "title": ["PERSONAL", "ASSISTANT AGENT"],
        "medium": "Agents, memory & your calendar",
        "lines": [
            "An assistant for the errands of a working",
            "week — inbox, calendar, follow-ups. It does the",
            "legwork; you approve what leaves your name.",
        ],
        "status": "IN THE STUDIO", "live": False,
    },
]


def work(i, w):
    W, H = 1200, 500
    left = w["side"] == "left"
    fx, fy = (64, 48) if left else (736, 48)
    cx, cy, cw, ch = (528, 62, 604, 376) if left else (64, 62, 604, 376)
    ox, oy = fx + 18, fy + 18
    wall_paint = (f'<g filter="url(#gouache)"><circle cx="{cx + cw - 40}" cy="{H + 40}" r="150" fill="{w["accent"]}" fill-opacity=".85"/></g>'
                  f'<g filter="url(#imp)">{stroke(f"M{cx - 30} 34 C{cx + 80} 18 {cx + 180} 42 {cx + 260} 24", w["stroke"], 40)}</g>')
    title = "".join(text(cx + 34, cy + 82 + j * 58, s, 58, "poster", key=f"w{i}t{j}") for j, s in enumerate(w["title"]))
    desc = "".join(text(cx + 36, cy + 246 + j * 28, s, 20, "sans", INK) for j, s in enumerate(w["lines"]))
    dot = (f'<circle cx="{cx + 46}" cy="{cy + 336}" r="10" fill="{RED}" stroke="{INK}" stroke-width="2.5"/>' if w["live"]
           else f'<circle cx="{cx + 46}" cy="{cy + 336}" r="10" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    content = f"""
{wall_paint}
<rect x="{fx + 12}" y="{fy + 12}" width="400" height="400" fill="{INK}"/>
<rect x="{fx}" y="{fy}" width="400" height="400" fill="{INK}"/>
<clipPath id="canvas"><rect x="{ox}" y="{oy}" width="364" height="364"/></clipPath>
<g clip-path="url(#canvas)"><rect x="{ox}" y="{oy}" width="364" height="364" fill="{CANVAS}"/>{w["art"](ox, oy)}</g>
{board(cx, cy, cw, ch)}
{tape(cx + cw / 2, cy + 2, 120, -3)}
{title}
{text(cx + 36, cy + 182, "Ahmed Ali, 2026", 16, "mono", INK_SOFT)}
{text(cx + 36, cy + 206, w["medium"], 16, "mono", INK_SOFT, extra=' font-style="italic"')}
{desc}
{dot}
{text(cx + 66, cy + 342, w["status"], 15, "bold", INK, ls=1.6)}
<circle cx="{cx + cw - 6}" cy="{cy + 4}" r="44" fill="#fff"/>
<circle cx="{cx + cw - 1}" cy="{cy + 9}" r="38" fill="{INK}"/>
<circle cx="{cx + cw - 6}" cy="{cy + 4}" r="38" fill="{w["accent"]}" stroke="{INK}" stroke-width="4"/>
{text(cx + cw - 6, cy + 20, w["n"], 44, "poster", w["num"], anchor="middle")}
"""
    alt = f'{w["n"]}: {" ".join(w["title"]).title()} — {w["medium"]}. {" ".join(w["lines"])} {w["status"].title()}.'
    return panel(W, H, w["wall"], content, alt, seed=5 + i * 7)


# ---------------------------------------------------------------- palette

DABS = [
    (420, 300, YELLOW, "Python"), (548, 246, RED, "PyTorch"), (690, 232, ORANGE, "TensorFlow"),
    (836, 240, BLUE, "TypeScript"), (968, 268, TEAL, "Node.js"), (1074, 340, HOT, "React"),
    (1054, 446, VIOLET, "Swift"), (930, 478, LIME, "Core ML"), (790, 470, SKY, "MCP"), (640, 420, INK, "Claude Code"),
]

SHELF = [
    ("GOOGLE CLOUD ✓", WHITE, INK), ("AWS", YELLOW, INK), ("AZURE", SKY, INK), ("DOCKER", TEAL, INK),
    ("KUBERNETES", PINK, INK), ("POSTGRES", LIME, INK), ("MONGODB", ORANGE, INK),
]


def palette():
    W, H = 1200, 580
    board_d = ("M340 380 C340 250 480 200 660 200 C870 200 1130 250 1140 370 C1150 490 990 545 830 535 "
               "C730 529 710 485 650 485 C590 485 570 545 480 545 C390 545 340 480 340 380 Z "
               "M430 420 a40 32 0 1 0 80 0 a40 32 0 1 0 -80 0 Z")
    dabs = "".join(stroke(f"M{x - 16} {y + 2} C{x - 6} {y - 10} {x + 8} {y - 8} {x + 18} {y + 4}", c, 50) for x, y, c, _ in DABS)
    smears = "".join([
        stroke("M700 330 C760 316 820 340 880 324", "#ff7a5c", 34),
        stroke("M720 368 C790 356 850 380 920 362", "#8f7bff", 30),
        stroke("M780 300 C820 292 860 300 900 292", "#ffe36b", 24),
    ])
    labels = []
    for k, (x, y, _, name) in enumerate(DABS):
        svg, _ = sticker(x - text_w(f"dab{k}", 60) / 2 - 10, y + 30, name, INK, WHITE, f"dab{k}", size=13, ls=0.6, tilt=(-4, 3, -2, 4)[k % 4], h=30, pad=10)
        labels.append(svg)
    shelf, sx, sy = [], 64, 300
    for k, (name, fill, color) in enumerate(SHELF):
        est = text_w(f"shelf{k}", len(name) * (13 * 0.68 + 1)) + 24
        if sx + est > 312:
            sx, sy = 64, sy + 52
        svg, w = sticker(sx, sy, name, fill, color, f"shelf{k}", size=13, ls=1, tilt=(-2, 2, -1, 1.5)[k % 4], h=34, pad=12)
        shelf.append(svg)
        sx += w + 16
    tools_tag, _ = sticker(64, 176, "TOOLS I PAINT WITH", YELLOW, INK, "k-tools", size=15, ls=2.2, tilt=-3)
    content = f"""
<g filter="url(#gouache)"><circle cx="1130" cy="40" r="170" fill="{SKY}"/><circle cx="60" cy="600" r="150" fill="{VIOLET}"/></g>
{text(66, 152, "THE PALETTE", 124, "poster", INK, key="pal-shadow")}
{text(60, 146, "THE PALETTE", 124, "poster", WHITE, key="pal")}
{tools_tag}
{text(64, 284, "ALSO ON THE SHELF", 12, "mono", WHITE, ls=2)}
{"".join(shelf)}
<path d="{board_d}" transform="translate(12 12)" fill="{INK}" fill-rule="evenodd"/>
<path d="{board_d}" fill="#f6ead2" stroke="{INK}" stroke-width="6" fill-rule="evenodd"/>
<g filter="url(#imp)">{smears}{dabs}</g>
{"".join(labels)}
"""
    tools = ", ".join(n for *_, n in DABS) + "; also " + ", ".join(n.replace(" ✓", " (certified)").title() for n, *_ in SHELF)
    return panel(W, H, COBALT, content, f"The palette — tools I paint with: {tools}", seed=29)


# ---------------------------------------------------------------- footer

def footer():
    W, H = 1200, 320
    paint = "".join([
        stroke("M860 340 C940 250 1060 130 1240 70", RED, 120),
        stroke("M1010 340 C1070 290 1150 262 1240 252", YELLOW, 84),
        stroke("M900 46 C960 26 1040 36 1110 16", COBALT, 70),
        stroke("M800 120 C812 110 828 112 840 124", HOT, 44),
    ])
    contact = (f'<text xml:space="preserve" x="60" y="262" class="mono" font-size="19" fill="{WHITE}">me@lordamdal.com'
               f'<tspan fill="{YELLOW}">  ✶  </tspan>@theamdal on X<tspan fill="{PINK}">  ✶  </tspan>linkedin/lordamdal</text>')
    content = f"""
<g filter="url(#gouache)"><circle cx="1190" cy="-10" r="100" fill="{TEAL}"/><circle cx="760" cy="350" r="70" fill="{VIOLET}"/></g>
<g filter="url(#imp)">{paint}</g>
{text(56, 200, "SAY HI.", 170, "poster", WHITE, key="hi")}
{contact}
"""
    return panel(W, H, INK, content, "Say hi — me@lordamdal.com, @theamdal on X, linkedin/lordamdal", seed=41)


# ---------------------------------------------------------------- buttons

def button(key, label, fill, color, tilt):
    size, ls, pad, h = 17, 1.6, 22, 52
    w = text_w(key, len(label) * (size * 0.68 + ls)) + 2 * pad
    m = 14
    W, H = w + 2 * m + 6, h + 2 * m + 6
    body = f"""<g transform="rotate({tilt} {m + w / 2:.1f} {m + h / 2})">
<rect x="{m - 6}" y="{m - 6}" width="{w + 12:.1f}" height="{h + 12}" rx="12" fill="#fff"/>
<rect x="{m + 6}" y="{m + 6}" width="{w:.1f}" height="{h}" rx="7" fill="{INK}"/>
<rect x="{m}" y="{m}" width="{w:.1f}" height="{h}" rx="7" fill="{fill}" stroke="{INK}" stroke-width="4"/>
{text(m + pad, m + h / 2 + size * 0.36, label, size, "bold", color, ls=ls, key=key)}
</g>"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H}" viewBox="0 0 {W:.0f} {H}" role="img">
<title>{escape(label)}</title>
<style>{CSS}</style>
{body}
</svg>
"""


BUTTONS = {
    "btn-email": ("EMAIL ME →", RED, WHITE, -2),
    "btn-x": ("@THEAMDAL ON X", COBALT, WHITE, 1.5),
    "btn-linkedin": ("LINKEDIN", YELLOW, INK, -1),
    "btn-site": ("CHROMEBOOST.WORK ↗", TEAL, INK, 2),
    "btn-repo": ("★ CHROMEBOOST ON GITHUB", PINK, INK, -1.5),
    "btn-gcp": ("GOOGLE CLOUD PROFILE ↗", LIME, INK, 1.5),
}


def main():
    pages = {"hero": hero(), "palette": palette(), "footer": footer()}
    for i, w in enumerate(WORKS):
        pages[f"work-{w['n']}"] = work(i, w)
    pages.update({name: button(name, *args) for name, args in BUTTONS.items()})
    for name, content in pages.items():
        (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
        print(f"wrote assets/{name}.svg")


if __name__ == "__main__":
    main()
