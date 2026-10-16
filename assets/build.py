#!/usr/bin/env python3
"""Generates the SVG panels used by the profile README.

GitHub strips CSS, fonts and scripts from READMEs, so every designed piece of the
page is an SVG image instead. Edit the copy below and run:

    python3 assets/build.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent

# Palette and type, lifted from chromeboost.work
INK, INK_SOFT = "#14110d", "#4a4239"
PAPER, PAPER_2, PAPER_3, CARD = "#f2ece0", "#e9e0cd", "#ded2ba", "#fbf8f1"
CORAL, ULTRA, VIRIDIAN = "#e2603c", "#2d49ab", "#2e7a58"
TEAL, NAPLES, ROSE, VIOLET = "#3ba0b2", "#efb63d", "#cd4f7c", "#6a4dad"

SANS = "'Helvetica Neue', Helvetica, Inter, 'Segoe UI', Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

BOLT = "M36 3 L12 36 h16 L26 61 L52 26 H35 Z"

FILTERS = """
<filter id="edge" x="-25%" y="-25%" width="150%" height="150%">
  <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="3" seed="11" result="t"/>
  <feDisplacementMap in="SourceGraphic" in2="t" scale="17" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="soft" x="-25%" y="-25%" width="150%" height="150%">
  <feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="3" seed="4" result="t"/>
  <feDisplacementMap in="SourceGraphic" in2="t" scale="26" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="torn" x="-10%" y="-30%" width="120%" height="160%">
  <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="7" result="t"/>
  <feDisplacementMap in="SourceGraphic" in2="t" scale="9" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" stitchTiles="stitch" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.08  0 0 0 0 0.066  0 0 0 0 0.05  0.22 0 0 0 -0.08"/>
</filter>
"""

CSS = f"""
.sans {{ font-family: {SANS}; }}
.mono {{ font-family: {MONO}; }}
.pre {{ white-space: pre; }}
@keyframes in {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""

# Rendered widths of headline runs in Helvetica Neue, measured in Chrome. They are
# pinned with textLength so other fonts (Arial on Windows) keep the same layout.
WIDTHS = {
    "h1a": 566, "h1b": 426.4, "h1c": 125.8, "h1d": 467.9,
    "n1": 309.3, "n2": 492.2, "p0": 594.8, "p1": 562.1, "p2": 519.2,
    "t1": 513, "f1": 764.7, "f2": 321.5, "marquee": 1475,
}


def mono_w(text, size, ls=0.0):
    return len(text) * (size * 0.602 + ls)


def pinned(key):
    w = WIDTHS.get(key)
    return f' textLength="{w}" lengthAdjust="spacingAndGlyphs"' if w else ""


def svg(w, h, body, title, extra_css=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<title>{escape(title)}</title>
<defs>{FILTERS}<clipPath id="clip"><rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="18"/></clipPath></defs>
<style>{CSS}{extra_css}</style>
{body}
</svg>
"""


def panel(w, h, body, title, bg=PAPER, extra_css=""):
    inner = f"""<g clip-path="url(#clip)">
<rect width="{w}" height="{h}" fill="{bg}"/>
{body}
<rect width="{w}" height="{h}" filter="url(#grain)"/>
</g>
<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="18" fill="none" stroke="{INK}" stroke-width="3"/>"""
    return svg(w, h, inner, title, extra_css)


def tag(x, y, label, fill=CARD, color=INK, size=13, ls=3.0, tilt=-1.5):
    """The boxed mono kicker that opens each section ("00 / TWO WAYS IN")."""
    w = mono_w(label, size, ls) + 34
    return f"""<g transform="rotate({tilt} {x} {y})">
<rect x="{x + 4}" y="{y + 4}" width="{w:.0f}" height="36" fill="{INK}"/>
<rect x="{x}" y="{y}" width="{w:.0f}" height="36" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>
<text x="{x + 17}" y="{y + 23}" class="mono" font-size="{size}" font-weight="700" letter-spacing="{ls}" fill="{color}">{escape(label)}</text>
</g>"""


def heading(x, y, text, size, key, color=INK, ls=None):
    ls = -0.045 * size if ls is None else ls
    return (f'<text id="{key}" x="{x}" y="{y}" class="sans" font-size="{size}" font-weight="900" '
            f'letter-spacing="{ls:.2f}" fill="{color}"{pinned(key)}>{escape(text)}</text>')


def highlight(x, y, text, size, key, fill, color):
    """A heading word on a torn strip of paint, like HANDS on the site."""
    w = WIDTHS.get(key, mono_w(text, size) * 1.05)
    return (f'<rect x="{x - 10}" y="{y - size * 0.8:.0f}" width="{w + 22:.0f}" height="{size * 0.94:.0f}" '
            f'fill="{fill}" filter="url(#torn)"/>' + heading(x, y, text, size, key, color))


def wash_sun(tx, ty, s=1.0, opacity=1.0):
    return f"""<g transform="translate({tx} {ty}) scale({s})" opacity="{opacity}">
<path d="M300 44 C400 8 530 52 580 148 C632 248 618 372 528 448 C438 524 300 540 206 486 C104 428 44 316 62 208 C80 100 196 82 300 44 Z" fill="{NAPLES}" opacity=".82" filter="url(#soft)"/>
<path d="M336 132 C412 108 486 158 502 236 C520 320 470 396 392 420 C310 446 224 404 202 330 C180 254 240 162 336 132 Z" fill="{CORAL}" opacity=".8" filter="url(#edge)"/>
<path d="M360 190 C420 176 470 214 474 266 C478 322 436 360 380 362 C322 364 290 322 292 272 C294 226 318 200 360 190 Z" fill="{ROSE}" opacity=".7" filter="url(#edge)"/>
</g>"""


def wash_pool(tx, ty, s=1.0, opacity=0.62):
    return f"""<g transform="translate({tx} {ty}) scale({s})" opacity="{opacity}">
<path d="M262 26 C368 6 458 84 478 186 C500 296 438 412 330 452 C218 494 92 440 54 340 C16 240 66 118 160 62 C196 40 222 34 262 26 Z" fill="{TEAL}" filter="url(#soft)"/>
</g>"""


def wash_dusk(tx, ty, s=1.0):
    return f"""<g transform="translate({tx} {ty}) scale({s})">
<path d="M234 18 C330 4 424 66 442 156 C462 252 396 330 296 342 C190 356 78 306 50 218 C24 134 108 40 234 18 Z" fill="{VIOLET}" opacity=".5" filter="url(#soft)"/>
<path d="M252 96 C316 86 366 128 368 184 C370 244 318 282 256 282 C194 282 148 240 150 184 C152 132 196 104 252 96 Z" fill="{VIRIDIAN}" opacity=".42" filter="url(#edge)"/>
</g>"""


# ---------------------------------------------------------------- hero

def hero():
    W, H = 1200, 630
    pill = "AI ENGINEER · BUILDING AGENTS"
    pill_w = 42 + mono_w(pill, 13, 2.6) + 16
    nav = "".join(
        f'<tspan dx="{0 if i == 0 else 30}">{t}</tspan>'
        for i, t in enumerate(["BROWSER AGENTS", "INFERENCE", "ASSISTANTS"])
    )
    sub = [
        [("Hi, I'm ", 0), ("Ahmed Ali", 1), (". I build AI agents that work in the", 0)],
        [("software you already use — ", 0), ("your browser, your inbox,", 1)],
        [("your week", 1), (" — and I make the models behind them", 0)],
        [("cheaper to run", 1), (", without making them any worse.", 0)],
    ]
    sub_svg = "".join(
        f'<text x="60" y="{466 + i * 34}" class="sans" font-size="23" fill="{INK_SOFT}">'
        + "".join(
            f'<tspan font-weight="700" fill="{INK}">{escape(t)}</tspan>' if b else escape(t)
            for t, b in line
        )
        + "</text>"
        for i, line in enumerate(sub)
    )

    term_x, term_y, term_w, term_h = 698, 258, 458, 262
    lines = [
        ("› what are you building right now?", INK, 700),
        ("→ a browser agent that drives real Chrome", INK_SOFT, 400),
        ("→ inference that costs less per task", INK_SOFT, 400),
        ("→ an assistant that runs my week", INK_SOFT, 400),
        ("→ live at chromeboost.work ✓", VIRIDIAN, 700),
    ]
    term_lines = "".join(
        f'<text class="mono l{i}" x="{term_x + 22}" y="{term_y + 82 + i * 31}" font-size="16" '
        f'font-weight="{wt}" fill="{c}">{escape(t)}</text>'
        for i, (t, c, wt) in enumerate(lines)
    )
    caret_y = term_y + 82 + len(lines) * 31
    css = "".join(
        f".l{i} {{ animation: in .45s ease-out {0.5 + i * 0.55:.2f}s backwards; }}\n" for i in range(1, len(lines))
    ) + ".caret { animation: blink 1.1s steps(1) infinite; }\n"

    body = f"""
{wash_pool(-300, 150)}
{wash_sun(690, -160, 0.92)}
{wash_dusk(700, 300)}
<path d="M690 196 C740 186 790 200 840 188 S930 170 990 176" fill="none" stroke="{ULTRA}" stroke-width="15" stroke-linecap="round" opacity=".5" filter="url(#edge)"/>
<rect width="{W}" height="76" fill="{PAPER}"/>

<rect x="59" y="23" width="38" height="38" fill="{INK}"/>
<rect x="56" y="20" width="38" height="38" fill="{NAPLES}" stroke="{INK}" stroke-width="2.5"/>
<path d="{BOLT}" transform="translate(63 27) scale(.375)" fill="{INK}"/>
<text x="108" y="48" class="sans" font-size="25" font-weight="700" letter-spacing="-.6" fill="{INK}">Ahmed Ali</text>
<text x="1144" y="45" text-anchor="end" class="mono" font-size="14" font-weight="700" letter-spacing="2.4" fill="{INK}">{nav}</text>
<rect x="0" y="76" width="{W}" height="3" fill="{INK}"/>

<g transform="rotate(-2 64 130)">
<rect x="68" y="116" width="{pill_w:.0f}" height="34" fill="{INK}"/>
<rect x="64" y="112" width="{pill_w:.0f}" height="34" fill="{TEAL}" stroke="{INK}" stroke-width="2.5"/>
<path d="{BOLT}" transform="translate(79 120) scale(.28)" fill="{INK}"/>
<text x="106" y="134" class="mono" font-size="13" font-weight="700" letter-spacing="2.6" fill="{INK}">{escape(pill)}</text>
</g>

{heading(58, 238, "AGENTS THAT", 88, "h1a")}
{highlight(58, 322, "ACTUALLY", 88, "h1b", CORAL, CARD)}
{heading(58 + WIDTHS.get("h1b", 430) + 26, 322, "DO", 88, "h1c")}
{heading(58, 406, "THE WORK.", 88, "h1d")}
{sub_svg}

<rect x="{term_x + 8}" y="{term_y + 8}" width="{term_w}" height="{term_h}" fill="{INK}"/>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fffcf5"/><stop offset="1" stop-color="#efe8f4"/></linearGradient>
<rect x="{term_x}" y="{term_y}" width="{term_w}" height="{term_h}" fill="url(#glass)" stroke="{INK}" stroke-width="3"/>
<rect x="{term_x}" y="{term_y}" width="{term_w}" height="44" fill="{INK}"/>
<circle cx="{term_x + 24}" cy="{term_y + 22}" r="6" fill="{CORAL}"/>
<circle cx="{term_x + 42}" cy="{term_y + 22}" r="6" fill="{NAPLES}"/>
<circle cx="{term_x + 60}" cy="{term_y + 22}" r="6" fill="{VIRIDIAN}"/>
<text x="{term_x + 80}" y="{term_y + 27}" class="mono" font-size="12.5" font-weight="700" letter-spacing="2.6" fill="{CARD}">YOU → AHMED</text>
<circle cx="{term_x + term_w - 66}" cy="{term_y + 22}" r="4" fill="{NAPLES}"/>
<circle cx="{term_x + term_w - 52}" cy="{term_y + 22}" r="4" fill="#6b635a"/>
<circle cx="{term_x + term_w - 38}" cy="{term_y + 22}" r="4" fill="#6b635a"/>
<circle cx="{term_x + term_w - 24}" cy="{term_y + 22}" r="4" fill="#6b635a"/>
{term_lines}
<text x="{term_x + 22}" y="{caret_y}" class="mono" font-size="16" font-weight="700" fill="{INK}">›</text>
<rect class="caret" x="{term_x + 42}" y="{caret_y - 14}" width="10" height="18" fill="{INK}"/>
"""
    return panel(W, H, body, "Ahmed Ali — agents that actually do the work", extra_css=css)


# ---------------------------------------------------------------- marquee

MARQUEE = [
    "Browser agents", "Real clicks, real sessions", "Cheaper inference",
    "Cost per task, not per token", "Personal assistants", "You approve what matters",
    "Open source",
]


def marquee():
    W, H = 1200, 60
    seq = "".join(f"{t}   ✦   " for t in MARQUEE)
    period = WIDTHS.get("marquee", 1500)
    css = f".run {{ animation: slide {period / 42:.0f}s linear infinite; }}\n@keyframes slide {{ to {{ transform: translateX(-{period}px); }} }}\n"
    copies = "".join(
        f'<text{' id="marquee"' if i == 0 else ''} x="{i * period}" y="37" class="sans pre" xml:space="preserve" font-size="17" '
        f'font-weight="700" fill="{INK}"{pinned("marquee")}>{escape(seq)}</text>'
        for i in range(2)
    )
    body = f'<g class="run">{copies}</g>'
    return panel(W, H, body, " · ".join(MARQUEE), bg=NAPLES, extra_css=css)


# ---------------------------------------------------------------- now building

PROJECTS = [
    {
        "color": CORAL, "num_color": CARD, "pill": "LIVE · CHROMEBOOST.WORK", "pill_fill": NAPLES,
        "title": "WEB BROWSER AUTOMATION AGENT",
        "lines": [
            "Gives Claude hands in your own Chrome — your logins, real clicks, real keystrokes.",
            "It reads, fills, drags and downloads; anything that posts, pays or deletes waits for you.",
        ],
        "chips": ["MCP server", "Chrome extension", "Claude Code", "Mac + Windows app", "MIT"],
    },
    {
        "color": NAPLES, "num_color": INK, "pill": "IN THE LAB", "pill_fill": TEAL,
        "title": "AI INFERENCE COST OPTIMISATION",
        "lines": [
            "Same answers, smaller bill. Finding where model spend actually goes and cutting it —",
            "measured in cost per finished task, not cost per token, with quality held fixed.",
        ],
        "chips": ["cost / task", "latency", "tokens", "quality evals"],
    },
    {
        "color": TEAL, "num_color": INK, "pill": "BUILDING", "pill_fill": CARD,
        "title": "PERSONAL ASSISTANT AI AGENT",
        "lines": [
            "An assistant for the errands of a working week — the inbox, the calendar, the",
            "follow-ups you'd forget. It does the legwork; you approve what leaves your name.",
        ],
        "chips": ["memory", "tool use", "scheduling", "human in the loop"],
    },
]


def project_card(i, p, y):
    x, w, h = 64, 1056, 214
    pill_w = mono_w(p["pill"], 12, 2.4) + 32
    chips, cx = [], x + 140
    for c in p["chips"]:
        cw = mono_w(c, 14.5, 0.4) + 22
        chips.append(
            f'<rect x="{cx:.0f}" y="{y + 162}" width="{cw:.0f}" height="31" rx="5" fill="{PAPER_2}" stroke="{INK}" stroke-width="1.5"/>'
            f'<text x="{cx + cw / 2:.0f}" y="{y + 183}" text-anchor="middle" class="mono" font-size="14.5" letter-spacing=".4" fill="{INK}">{escape(c)}</text>'
        )
        cx += cw + 10
    desc = "".join(
        f'<text x="{x + 140}" y="{y + 114 + j * 30}" class="sans" font-size="20.5" fill="{INK_SOFT}">{escape(t)}</text>'
        for j, t in enumerate(p["lines"])
    )
    return f"""
<rect x="{x + 8}" y="{y + 8}" width="{w}" height="{h}" fill="{INK}"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{CARD}" stroke="{INK}" stroke-width="3"/>
<rect x="{x + 1.5}" y="{y + 1.5}" width="106.5" height="{h - 3}" fill="{p["color"]}"/>
<rect x="{x + 107}" y="{y}" width="3" height="{h}" fill="{INK}"/>
<text x="{x + 54}" y="{y + 120}" text-anchor="middle" class="mono" font-size="38" font-weight="700" fill="{p["num_color"]}">{i + 1:02d}</text>
<rect x="{x + 140}" y="{y - 16}" width="{pill_w:.0f}" height="32" rx="16" fill="{p["pill_fill"]}" stroke="{INK}" stroke-width="2.5"/>
<text x="{x + 156}" y="{y + 4.5}" class="mono" font-size="12" font-weight="700" letter-spacing="2.4" fill="{INK}">{escape(p["pill"])}</text>
{heading(x + 140, y + 76, p["title"], 34, f"p{i}", ls=-1.2)}
{desc}
{"".join(chips)}"""


def now():
    W = 1200
    top, step = 386, 266
    H = top + step * (len(PROJECTS) - 1) + 214 + 64
    cards = "".join(project_card(i, p, top + i * step) for i, p in enumerate(PROJECTS))
    body = f"""
{wash_sun(940, -190, 0.62, 0.9)}
{wash_pool(-330, H - 300, 0.9, 0.5)}
{tag(64, 52, "00 / NOW BUILDING")}
{heading(60, 172, "ONE IDEA.", 66, "n1")}
{heading(60, 238, "THREE WAYS IN.", 66, "n2")}
<text x="62" y="292" class="sans" font-size="22" fill="{INK_SOFT}">The idea: AI that does <tspan font-weight="700" fill="{INK}">real work</tspan> for you — in your browser, across your week —</text>
<text x="62" y="324" class="sans" font-size="22" fill="{INK_SOFT}">and costs little enough to run that you <tspan font-weight="700" fill="{INK}">actually leave it on.</tspan></text>
{cards}
"""
    return panel(W, H, body, "Now building: a web browser automation agent, AI inference cost optimisation, and a personal assistant agent")


# ---------------------------------------------------------------- toolbox

TOOLBOX = [
    ("AI / ML", [("Python", NAPLES), ("PyTorch", CORAL), ("TensorFlow", None), ("MCP", TEAL), ("Claude Code", None), ("Core ML", None)]),
    ("APPS", [("TypeScript", TEAL), ("Node.js", None), ("React", None), ("Swift", None), ("Flutter", None), (".NET", None)]),
    ("INFRA", [("Google Cloud ✓", NAPLES), ("AWS", None), ("Azure", None), ("Docker", None), ("Kubernetes", None), ("PostgreSQL", None), ("MongoDB", None)]),
]


def toolbox():
    W = 1200
    rows = []
    for r, (label, items) in enumerate(TOOLBOX):
        y = 196 + r * 62
        rows.append(f'<text x="64" y="{y + 26}" class="mono" font-size="13" font-weight="700" letter-spacing="2.4" fill="{INK_SOFT}">{label}</text>')
        x = 190
        for name, fill in items:
            w = mono_w(name, 17, 0.3) + 30
            rows.append(
                f'<rect x="{x + 3:.0f}" y="{y + 3}" width="{w:.0f}" height="40" fill="{INK}"/>'
                f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="40" fill="{fill or CARD}" stroke="{INK}" stroke-width="2"/>'
                f'<text x="{x + w / 2:.0f}" y="{y + 26}" text-anchor="middle" class="mono" font-size="17" font-weight="700" letter-spacing=".3" fill="{INK}">{escape(name)}</text>'
            )
            x += w + 14
    H = 196 + 62 * len(TOOLBOX) + 36
    body = f"""
{wash_dusk(930, -70, 0.8)}
{tag(64, 52, "01 / TOOLBOX", fill=NAPLES)}
{heading(60, 166, "WHAT I REACH FOR.", 56, "t1")}
{"".join(rows)}
"""
    tools = "; ".join(f"{label}: " + ", ".join(n for n, _ in items) for label, items in TOOLBOX)
    return panel(W, H, body, f"Toolbox — {tools}")


# ---------------------------------------------------------------- footer

def footer():
    W, H = 1200, 340
    contact = "".join(
        f'<tspan dx="{0 if i == 0 else 22}">{escape(t)}</tspan>'
        for i, t in enumerate(["ME@LORDAMDAL.COM", "✦", "@THEAMDAL ON X", "✦", "IN/LORDAMDAL"])
    )
    body = f"""
{wash_sun(860, -40, 0.8, 0.95)}
<g transform="rotate(-1.5 64 52)">
<rect x="64" y="52" width="{mono_w("02 / SAY HELLO", 13, 3) + 34:.0f}" height="36" fill="none" stroke="{NAPLES}" stroke-width="2.5"/>
<text x="81" y="75" class="mono" font-size="13" font-weight="700" letter-spacing="3" fill="{NAPLES}">02 / SAY HELLO</text>
</g>
{heading(60, 172, "GOT A JOB FOR AN AGENT?", 60, "f1", color=CARD)}
{highlight(60, 246, "LET'S TALK.", 60, "f2", NAPLES, INK)}
<text x="62" y="300" class="mono" font-size="14" font-weight="700" letter-spacing="2.4" fill="{NAPLES}">{contact}</text>
"""
    return panel(W, H, body, "Got a job for an agent? Let's talk — me@lordamdal.com, @theamdal on X", bg=INK)


# ---------------------------------------------------------------- buttons

def button(label, fill, color, shadow=INK):
    size, ls = 15, 2.6
    w = mono_w(label, size, ls) + 56
    body = f"""<rect x="7.5" y="7.5" width="{w:.0f}" height="50" fill="{shadow}"/>
<rect x="1.5" y="1.5" width="{w:.0f}" height="50" fill="{fill}" stroke="{INK}" stroke-width="3"/>
<text x="{1.5 + w / 2 + ls / 2:.1f}" y="32" text-anchor="middle" class="mono" font-size="{size}" font-weight="700" letter-spacing="{ls}" fill="{color}">{escape(label)}</text>"""
    return svg(round(w + 9), 60, body, label)


BUTTONS = {
    "btn-email": ("ME@LORDAMDAL.COM", CORAL, INK),
    "btn-x": ("@THEAMDAL ON X", INK, NAPLES),
    "btn-linkedin": ("LINKEDIN", CARD, INK),
    "btn-site": ("CHROMEBOOST.WORK ↗", CARD, INK),
    "btn-repo": ("★ CHROMEBOOST ON GITHUB", INK, NAPLES),
    "btn-gcp": ("GOOGLE CLOUD PROFILE ↗", CARD, INK),
}


def main():
    pages = {"hero": hero(), "marquee": marquee(), "now": now(), "toolbox": toolbox(), "footer": footer()}
    pages.update({name: button(*args) for name, args in BUTTONS.items()})
    # GitHub's dark theme swallows ink shadows, so <picture> swaps in these
    pages.update({f"{name}-dark": button(*args, shadow=PAPER_3) for name, args in BUTTONS.items()})
    for name, content in pages.items():
        (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
        print(f"wrote assets/{name}.svg")


if __name__ == "__main__":
    main()
