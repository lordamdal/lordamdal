#!/usr/bin/env python3
"""Builds the SVG blocks used by the profile README.

GitHub strips CSS, fonts and scripts from READMEs, so every designed block is an
SVG image. The look is minimal neo-brutalism: cream paper, black ink, one yellow
accent, thick borders and hard offset shadows, and nothing else. Yellow marks
what is live or clickable. Edit the copy below and run:

    python3 assets/build.py             # write the SVGs
    python3 assets/build.py --measure   # re-measure pinned text in Chrome first

Text that drives layout (the headline marks, titles, tags, buttons) is pinned
with textLength to its width as Chrome on macOS renders it (widths.json), so
fallback fonts keep the layout. New copy without a measured width uses an
estimate until you run --measure.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent
WIDTHS_FILE = OUT / "widths.json"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

INK, PAPER, YELLOW, MUTED, WHITE = "#111111", "#f6f2e9", "#ffd400", "#5d5950", "#ffffff"

SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', SFMono-Regular, ui-monospace, Menlo, Consolas, monospace"
FONTS = {"d": (SANS, 700), "s": (SANS, 400), "m": (MONO, 400), "mb": (MONO, 700)}
CSS = " ".join(f".{k} {{ font-family: {f}; font-weight: {w}; }}" for k, (f, w) in FONTS.items())
EST = {"d": 0.6, "s": 0.5, "m": 0.6, "mb": 0.6}  # average advance per em, for unmeasured text

BORDER, SHADOW, HALO = 5, 10, 3
CELL = 168  # width of the left index column shared by every block below the hero

WIDTHS = json.loads(WIDTHS_FILE.read_text(encoding="utf-8")) if WIDTHS_FILE.exists() else {}
PINNED = {}  # runs measured for this build: key -> (cls, size, ls, text)


# ---------------------------------------------------------------- copy

HERO = {
    "name": "AMDAL",
    "role": "AI ENGINEER",
    # *word* gets a yellow mark; each one names a card below.
    "lines": ["I give AI *hands*,", "a *voice* and *eyes*."],
    "sub": "Agents that work where people already are: in the browser, out loud, on camera.",
}

WORK = [
    {
        "n": "01", "title": "HANDS", "project": "CHROMEBOOST", "flagship": True,
        "tag": "LIVE — CHROMEBOOST.WORK ↗",
        "lines": [
            "Lets Claude Code, Codex or Gemini CLI drive your real, logged-in Chrome.",
            "The hard part isn't the clicking. It's knowing when to stop and ask.",
        ],
    },
    {
        "n": "02", "title": "VOICE", "project": "VOICE RAG", "flagship": False,
        "tag": "OPEN SOURCE ↗",
        "lines": [
            "A voice assistant that runs entirely on a laptop: Whisper, a local LLM and",
            "Kokoro, streaming sentence by sentence. Nothing leaves the machine.",
        ],
    },
    {
        "n": "03", "title": "EYES", "project": "SIGNLINK + AVATARS", "flagship": False,
        "tag": "OPEN SOURCE ↗",
        "lines": [
            "Sign language recognised live from a webcam with MediaPipe and an LSTM.",
            "Now: video avatars that answer fast enough to feel like a conversation.",
        ],
    },
]

MIND = {
    "label": "ON MY MIND",
    "questions": [
        "How much should an agent do in your real accounts before it asks?",
        "How fast must a voice agent answer before it stops feeling like a machine?",
        "What does one finished task really cost when an agent does it?",
    ],
}

TALK = {
    "label": "LET'S TALK",
    "lines": [
        "If you're building agents that touch the real world,",
        "or you've answered one of these better than I have,",
        "I'd like to compare notes.",
    ],
    "cta": "ME@LORDAMDAL.COM →",
}

BUTTONS = {
    "btn-x": ("X / @THEAMDAL", PAPER),
    "btn-linkedin": ("LINKEDIN ↗", PAPER),
}


# ---------------------------------------------------------------- primitives

def run_key(s, size, cls, ls):
    return f"{cls}|{size}|{ls}|{s}"


def width(s, size, cls="s", ls=0, measure=False):
    key = run_key(s, size, cls, ls)
    if measure:
        PINNED[key] = (cls, size, ls, s)
    return WIDTHS.get(key, len(s) * (size * EST[cls] + ls))


def text(x, y, s, size, cls="s", fill=INK, anchor=None, ls=0, pin=False):
    attrs = f'x="{x:g}" y="{y:g}" class="{cls}" font-size="{size}" fill="{fill}"'
    if anchor:
        attrs += f' text-anchor="{anchor}"'
    if ls:
        attrs += f' letter-spacing="{ls}"'
    if pin:
        key = run_key(s, size, cls, ls)
        PINNED[key] = (cls, size, ls, s)
        if key in WIDTHS:
            attrs += f' textLength="{WIDTHS[key]}" lengthAdjust="spacingAndGlyphs"'
    return f"<text {attrs}>{escape(s)}</text>"


def block(x, y, w, h, fill, border=BORDER, shadow=0):
    """Flat box whose ink border sits inside x..x+w, with an optional hard shadow."""
    b = border
    out = f'<rect x="{x + shadow:g}" y="{y + shadow:g}" width="{w:g}" height="{h:g}" fill="{INK}"/>' if shadow else ""
    return out + (f'<rect x="{x + b / 2:g}" y="{y + b / 2:g}" width="{w - b:g}" height="{h - b:g}" '
                  f'fill="{fill}" stroke="{INK}" stroke-width="{b}"/>')


def svg(w, h, shadow, body, title):
    """Wraps a w×h shape that casts a hard shadow. The white halo round the shape and
    its shadow is invisible on GitHub's light theme and keeps both readable on dark."""
    W, H = w + shadow + 2 * HALO, h + shadow + 2 * HALO
    halo = "".join(f'<rect x="{o - HALO}" y="{o - HALO}" width="{w + 2 * HALO}" height="{h + 2 * HALO}" fill="{WHITE}"/>'
                   for o in (0, shadow))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:g}" height="{H:g}" viewBox="0 0 {W:g} {H:g}" role="img">
<title>{escape(title)}</title>
<style>{CSS}</style>
<g transform="translate({HALO} {HALO})">
{halo}<rect x="{shadow}" y="{shadow}" width="{w:g}" height="{h:g}" fill="{INK}"/>
{body}
</g>
</svg>
"""


def card(w, h, inner, title, fill=PAPER):
    """A panel: flat fill, a thick ink border drawn over its contents, a hard shadow."""
    b = BORDER
    body = (f'<rect width="{w}" height="{h}" fill="{fill}"/>\n{inner}\n'
            f'<rect x="{b / 2}" y="{b / 2}" width="{w - b}" height="{h - b}" fill="none" stroke="{INK}" stroke-width="{b}"/>')
    return svg(w, h, SHADOW, body, title)


def tag(right, y, label, live):
    """A small label box flush right at x=right. Live tags are yellow and cast a shadow."""
    size, ls, pad, h = 16, 1.5, 18, 44
    w = width(label, size, "mb", ls) + 2 * pad
    x = right - w
    return block(x, y, w, h, YELLOW if live else PAPER, 3, 5 if live else 0) + text(
        x + pad, y + h / 2 + size * 0.36, label, size, "mb", ls=ls, pin=True)


def index_cell(h, fill, label=None):
    """The left column: a fill, an ink rule, and an optional small caps label."""
    out = f'<rect width="{CELL}" height="{h}" fill="{fill}"/><rect x="{CELL}" width="{BORDER}" height="{h}" fill="{INK}"/>'
    if label:
        out += text(CELL / 2, h / 2 + 6, label, 15, "mb", anchor="middle", ls=2.5)
    return out


def marked_line(x, y, line, size, ls):
    """A headline line whose *starred* words sit on yellow marks; returns (svg, plain text)."""
    plain = line.replace("*", "")
    marks = []
    for m in re.finditer(r"\*([^*]+)\*", line):
        prefix = line[:m.start()].replace("*", "")
        mx = x + (width(prefix, size, "d", ls, measure=True) if prefix else 0)
        mw = width(m.group(1), size, "d", ls, measure=True)
        # Borderless on purpose: an ink edge through the letters reads as strikethrough.
        marks.append(f'<rect x="{mx - 2:g}" y="{y - 28:g}" width="{mw + 4:g}" height="44" fill="{INK}"/>'
                     f'<rect x="{mx - 8:g}" y="{y - 34:g}" width="{mw + 4:g}" height="44" fill="{YELLOW}"/>')
    return "".join(marks) + text(x, y, plain, size, "d", ls=ls, pin=True), plain


def plain_title(c):
    return f'{c["n"]}, {c["title"].capitalize()}: {c["project"].title().replace("Rag", "RAG")}.'


# ---------------------------------------------------------------- blocks

def hero():
    w, h, x, size, ls = 1200, 500, 60, 108, -3
    lines, plain = [], []
    for i, line in enumerate(HERO["lines"]):
        svg_line, text_line = marked_line(x, 222 + i * 124, line, size, ls)
        lines.append(svg_line)
        plain.append(text_line)
    inner = f"""{text(x, 62, HERO["name"], 34, "d", ls=1)}
{text(w - x, 59, HERO["role"], 17, "mb", anchor="end", ls=2.5)}
<rect y="96" width="{w}" height="{BORDER}" fill="{INK}"/>
{"".join(lines)}
{text(x, 438, HERO["sub"], 26, "s")}"""
    return card(w, h, inner, f'{HERO["name"].title()}, {HERO["role"].lower()}. {" ".join(plain)} {HERO["sub"]}')


def work(c):
    w, h = 1200, 196
    x = CELL + BORDER + 38
    lines = "".join(text(x, 118 + j * 30, s, 22, "s") for j, s in enumerate(c["lines"]))
    px = x + width(c["title"], 40, "d", -0.5) + 20
    inner = f"""{index_cell(h, YELLOW if c["flagship"] else PAPER)}
{text(CELL / 2, h / 2 + 24, c["n"], 68, "d", anchor="middle", ls=-2)}
{text(x, 76, c["title"], 40, "d", ls=-0.5, pin=True)}
{text(px, 76, "/ " + c["project"], 16, "mb", MUTED, ls=1.5)}
{lines}
{tag(w - 36, 40, c["tag"], True)}"""
    return card(w, h, inner, f'{plain_title(c)} {" ".join(c["lines"])} {c["tag"].replace(" ↗", "").capitalize()}.')


def mind():
    w, h, gap = 1200, 204, 46
    x = CELL + BORDER + 38
    rows = "".join(block(x, 56 + j * gap, 14, 14, YELLOW, 3) + text(x + 32, 70 + j * gap, q, 22, "s")
                   for j, q in enumerate(MIND["questions"]))
    inner = f"{index_cell(h, PAPER, MIND['label'])}\n{rows}"
    return card(w, h, inner, f'{MIND["label"].capitalize()}: {" ".join(MIND["questions"])}')


def talk():
    w, h = 1200, 284
    x = CELL + BORDER + 38
    lines = "".join(text(x, 78 + j * 42, s, 30, "d", ls=-0.5) for j, s in enumerate(TALK["lines"]))
    size, ls, pad = 18, 1.5, 22
    cw = width(TALK["cta"], size, "mb", ls) + 2 * pad
    inner = f"""{index_cell(h, YELLOW, TALK["label"])}
{lines}
{block(x, 192, cw, 54, PAPER, 4, 6)}
{text(x + pad, 192 + 27 + size * 0.36, TALK["cta"], size, "mb", ls=ls, pin=True)}"""
    email = TALK["cta"].replace(" →", "").lower()
    return card(w, h, inner, f'{TALK["label"].capitalize()}. {" ".join(TALK["lines"])} Email {email}.', fill=YELLOW)


def button(label, fill):
    size, ls, pad, h, b, sh = 16, 1.5, 24, 50, 4, 6
    w = width(label, size, "mb", ls) + 2 * pad
    body = block(0, 0, w, h, fill, b) + text(pad, h / 2 + size * 0.36, label, size, "mb", ls=ls, pin=True)
    return svg(w, h, sh, body, label)


# ---------------------------------------------------------------- build

def build():
    PINNED.clear()
    pages = {"hero": hero()}
    pages.update({f"work-{c['n']}": work(c) for c in WORK})
    pages.update({"mind": mind(), "talk": talk()})
    pages.update({name: button(*args) for name, args in BUTTONS.items()})
    return pages


def measure():
    """Renders every pinned run in headless Chrome and saves the widths to widths.json."""
    build()
    runs = sorted(PINNED.items())
    texts = "".join(f'<text xml:space="preserve" class="{c}" font-size="{z}" letter-spacing="{l}" y="100">{escape(s)}</text>'
                    for _, (c, z, l, s) in runs)
    page = (f'<!doctype html><meta charset="utf-8"><svg xmlns="http://www.w3.org/2000/svg" width="4000" height="200">'
            f"<style>{CSS}</style>{texts}</svg><pre id=\"out\"></pre><script>document.fonts.ready.then(() => "
            "{ out.textContent = JSON.stringify([...document.querySelectorAll('text')]"
            ".map(t => +t.getComputedTextLength().toFixed(1))); });</script>")
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "measure.html"
        html.write_text(page, encoding="utf-8")
        dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={tmp}/profile",
                              "--virtual-time-budget=5000", "--dump-dom", html.as_uri()],
                             capture_output=True, text=True, check=True).stdout
    widths = json.loads(dom.split('<pre id="out">')[1].split("</pre>")[0])
    WIDTHS.clear()
    WIDTHS.update({key: wd for (key, _), wd in zip(runs, widths)})
    WIDTHS_FILE.write_text(json.dumps(WIDTHS, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"measured {len(WIDTHS)} runs -> assets/widths.json")


def main():
    if "--measure" in sys.argv[1:]:
        measure()
    for name, content in build().items():
        (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
        print(f"wrote assets/{name}.svg")


if __name__ == "__main__":
    main()
