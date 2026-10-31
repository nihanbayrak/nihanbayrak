"""The introduction, set as a printed sheet under the octopus plate.

Era: victorian-automaton-3d, from the brass-and-enamel octopus automaton in the
moodboard (Screenshot 2026-08-27 at 11.25.54) — one built object on a cream
ground with one soft shadow. The page under it is set like the 1922 Ladies'
Home Journal page: a ruled panel of small-caps facts, a hairline rule between
columns, a drop cap.

Signature: clockwork. The automaton's own mechanism is wound, stepped and
repeating, so the headline does not bounce or glide. Every letter steps up and
back through held positions, about ten a second, and the step runs through the
line like a cam turning. It is the only thing on the sheet that moves: the
display line carries the motion and the reading text holds still. Everything is
in place at first paint, and reduced motion gets the line at rest.

Three values: paper, tobacco ink, oxblood. Grain on the paper, because nothing
ships flat. Cormorant Infant Light is the character; Libre Baskerville does the
reading; Archivo Narrow carries the facts.

A README allows no script and no hover, so all of this is CSS inside the image.
The type has to be outlines (see typeset.py). Each glyph is drawn once in <defs>
and placed with <use>. The README picks the narrow cut at 600 px and under,
where the wide one would shrink the type below reading size.

Needs fonttools and uharfbuzz, which the workflow does not install, so the
Action never calls this. Run it by hand and commit both SVGs. The README's alt
text repeats this copy; change both together.
"""
import math
import random
from pathlib import Path

import typeset

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Yves Klein: International Klein Blue as the ground, white type, and gold, the
# third of his colours and the brass of the octopus, as the one accent. Every
# piece carries its own ground now, so one version serves both GitHub themes.
GROUND = "#002FA7"
THEMES = {
    "klein": dict(ink="#FFFFFF", structure="#D9B44A"),
}

HEADLINE = "Care is my building language."
ACCENT_WORD = "Care"
DECK = ("Writing code is becoming the easy part; deciding what to build, and why, is now "
        "the bottleneck.")
BODY = [
    "The time AI gives back, I spend on judgment: a clear spec before the build, a measure "
    "of whether it worked after, and the honesty to rethink the whole system when the "
    "numbers say it is wrong. The models are getting better quickly, which makes taste and "
    "care more valuable, not less.",
]
NAME, PLACE = "NIHAN BAYRAK", "BERLIN"
ROLES = ["AI SPECIALIST", "PRODUCT MANAGER", "SOLUTIONS ENGINEER"]
DAY_LABEL, DAY = "BY DAY", "WIN CREATING IMAGES"

DISPLAY, READING, FACT, FACT_BOLD = "display", "body", "fact", "fact_bold"
TRACK = 0.1                            # small caps get air; body never does

LAYOUTS = {
    "wide": dict(W=800, pad=44, top=44, panel=164, gutter=24, head=60, deck=23, deck_lead=31,
                 body=15.5, lead=26, fact=11.5, fact_lead=18),
    "narrow": dict(W=380, pad=22, top=28, panel=None, gutter=0, head=46, deck=20, deck_lead=27,
                   body=14.5, lead=24, fact=11, fact_lead=17),
}

CYCLE = 4.0                            # seconds between turns of the cam
STEP = 0.07                            # one letter to the next

STYLE = f"""
.t {{ transform-box: fill-box; transform-origin: 50% 100%;
      animation: tick {CYCLE}s steps(1, end) infinite; }}
.t.r {{ animation-name: tick-r; }}
@keyframes tick {{
  0%, 10%, 100% {{ transform: none; }}
  2.5% {{ transform: translateY(-7px) rotate(-5deg); }}
  5%   {{ transform: translateY(-14px) rotate(4deg); }}
  7.5% {{ transform: translateY(-5px) rotate(-2deg); }}
}}
@keyframes tick-r {{
  0%, 10%, 100% {{ transform: none; }}
  2.5% {{ transform: translateY(-7px) rotate(5deg); }}
  5%   {{ transform: translateY(-14px) rotate(-4deg); }}
  7.5% {{ transform: translateY(-5px) rotate(2deg); }}
}}
@media (prefers-reduced-motion: reduce) {{ .t {{ animation: none; }} }}
"""


# ---------------------------------------------------------------- the kaleidoscope

SEGMENTS, PIECES = 12, 56
WEDGE = math.tau / SEGMENTS


def _rand(i, k):
    return random.Random(f"{i}:{k}").random()


def kaleidoscope(W, H, cx, cy):
    """Yao's kaleidoscope, in SVG: hexagram bars and square-holed coins laid in one
    30 degree wedge and mirrored twelve times. The tube turns slowly and the pieces
    drift inside the mirrors, so every piece meets its reflection as it moves.
    Tones of the ground's own blue, plus a little gold and white, quiet enough that
    the words lead. Returns (defs, body)."""
    R = math.hypot(max(cx, W - cx), max(cy, H - cy)) * 1.05
    unit = R * 0.32
    tones = [("#1B4DC7", .8), ("#D9B44A", .16), ("#FFFFFF", .07)]
    pieces = []
    for i in range(PIECES):
        coin = i % 5 == 0
        r = (0.04 + _rand(i, 1) * 0.96) * R * 0.7
        a = (_rand(i, 2) * 1.8 - 0.4) * WEDGE      # wider than the mirror: no empty edge
        grow = 0.45 + (r / R) * 1.2
        w = (unit * (0.08 + _rand(i, 3) * 0.1) if coin else unit * (0.16 + _rand(i, 3) * 0.4)) * grow
        h = w if coin else unit * (0.035 + _rand(i, 4) * 0.035) * grow
        x, y, rot = math.cos(a) * r, math.sin(a) * r, math.degrees(_rand(i, 5) * math.pi)
        colour, alpha = tones[i % 3]
        at = f'transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})" fill="{colour}" fill-opacity="{alpha}"'
        if coin:
            hole = w * 0.28
            pieces.append(f'<path fill-rule="evenodd" {at} d="M{-w / 2:.1f} 0a{w / 2:.1f} {w / 2:.1f} 0 1 0 {w:.1f} 0'
                          f'a{w / 2:.1f} {w / 2:.1f} 0 1 0 {-w:.1f} 0Z M{-hole / 2:.1f} {-hole / 2:.1f}h{hole:.1f}v{hole:.1f}'
                          f'h{-hole:.1f}Z"/>')
        else:
            pieces.append(f'<rect {at} x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" '
                          f'rx="{h / 2.5:.1f}"/>')
    tip = R * 1.1
    wedge = (f'<clipPath id="kw" clipPathUnits="userSpaceOnUse"><path d="M0 0L{tip:.0f} 0'
             f'L{tip * math.cos(WEDGE):.0f} {tip * math.sin(WEDGE):.0f}Z"/></clipPath>')
    defs = wedge + f'<g id="kp">{"".join(pieces)}</g>'
    mirrors = []
    for i in range(SEGMENTS):
        # Odd segments are mirror images, as in Yao.
        if i % 2 == 0:
            turn = f"rotate({math.degrees(i * WEDGE):.0f})"
        else:
            turn = f"rotate({math.degrees((i + 1) * WEDGE):.0f}) scale(1 -1)"
        mirrors.append(f'<g transform="{turn}"><g clip-path="url(#kw)"><g class="kd">'
                       f'<use xlink:href="#kp"/></g></g></g>')
    body = f'<g transform="translate({cx:.0f} {cy:.0f})"><g class="ks">{"".join(mirrors)}</g></g>'
    # Fade it in and out at the top and bottom, so on the one-image page it has no
    # edge where the piece above meets it. Ground-coloured veils: cheaper than a mask.
    fade = 70
    defs += (f'<linearGradient id="kv" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{GROUND}"/><stop offset="1" stop-color="{GROUND}" stop-opacity="0"/>'
             f'</linearGradient>')
    body += (f'<rect width="{W}" height="{fade}" fill="url(#kv)"/>'
             f'<rect width="{W}" height="{fade}" fill="url(#kv)" transform="translate(0 {H}) scale(1 -1)"/>')
    return defs, body


KALEIDOSCOPE_STYLE = """
.ks { animation: tube 140s linear infinite; }
.kd { animation: drift 16s ease-in-out infinite alternate; }
@keyframes tube { to { transform: rotate(360deg); } }
@keyframes drift { from { transform: none; } to { transform: translate(22px, 14px) rotate(7deg); } }
@media (prefers-reduced-motion: reduce) { .ks, .kd { animation: none; } }
"""


class Sheet:
    """Outlines placed on a page. Every glyph is drawn once and reused."""

    def __init__(self, ink, structure):
        self.ink, self.structure = ink, structure
        self.under = ""                              # on the ground, under everything else
        self.ids, self.defs, self.marks = {}, [], []

    def _ref(self, face, name):
        key = (face, name)
        if key not in self.ids:
            _, glyphset, _, _ = typeset._load(face)
            pen = typeset.SVGPathPen(glyphset, ntos=lambda v: str(int(round(v))))
            glyphset[name].draw(pen)
            d = pen.getCommands()
            self.ids[key] = f"g{len(self.defs)}" if d else None
            if d:
                self.defs.append(f'<path id="{self.ids[key]}" d="{d}"/>')
        return self.ids[key]

    def glyphs(self, text, face, size, x, y, tracking=0.0):
        """[(svg <use>, glyph index in text)] and the run's width in px."""
        _, _, _, upem = typeset._load(face)
        placed, adv = typeset.shape(text, face, tracking)
        s = size / upem
        out = []
        for i, (name, gx) in enumerate(placed):
            gid = self._ref(face, name)
            if gid:
                out.append((f'<use xlink:href="#{gid}" transform="translate({x + gx * s:.2f} {y:.2f}) '
                            f'scale({s:.5f} {-s:.5f})"/>', i))
        return out, adv * s

    def text(self, text, face, size, x, y, fill, tracking=0.0, anchor="start"):
        uses, width = self.glyphs(text, face, size, 0, 0, tracking)
        if anchor == "end":
            x -= width
        uses, width = self.glyphs(text, face, size, x, y, tracking)
        self.marks.append(f'<g fill="{fill}">{"".join(u for u, _ in uses)}</g>')
        return width

    def rule(self, x0, y0, x1, y1, colour, weight=0.75):
        self.marks.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                          f'stroke="{colour}" stroke-width="{weight}"/>')

    def svg(self, W, H, alt, title=HEADLINE, style=STYLE):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img" aria-label="{alt}">'
                f'<title>{title}</title><style>{style}</style><defs>{"".join(self.defs)}</defs>'
                f'<rect width="{W}" height="{H:.0f}" fill="{GROUND}"/>{self.under}'
                f'{"".join(self.marks)}</svg>')


def _wrap_varying(words, face, size, width_for_line):
    """Greedy breaking where each line can have its own measure."""
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if cur and typeset.measure(trial, face, size) > width_for_line(len(lines)):
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def headline(sh, x, y, width, size):
    """The moving line, glyph by glyph. Returns the baseline after it."""
    lines = typeset.wrap(HEADLINE, DISPLAY, size, width)
    letter = 0
    for line in lines:
        uses, _ = sh.glyphs(line, DISPLAY, size, x, y)
        drawn = {i: u for u, i in uses}
        _, _, _, upem = typeset._load(DISPLAY)
        for i in range(len(typeset.shape(line, DISPLAY)[0])):
            if i in drawn:
                fill = sh.structure if letter < len(ACCENT_WORD) else sh.ink
                side = " r" if letter % 2 else ""
                sh.marks.append(f'<g class="t{side}" fill="{fill}" '
                                f'style="animation-delay:{.3 + letter * STEP:.2f}s">{drawn[i]}</g>')
            letter += 1
        y += size * 1.0
    return y - size * 1.0


def prose(sh, L, x, y, width):
    """Deck, then body with a drop cap. Returns the last baseline."""
    for line in typeset.wrap(DECK, DISPLAY, L["deck"], width):
        sh.text(line, DISPLAY, L["deck"], x, y, sh.ink)
        y += L["deck_lead"]
    y += L["lead"] * 0.55

    body, lead = L["body"], L["lead"]
    for p, para in enumerate(BODY):
        if p == 0:
            # Drop cap: from the cap height of line one to the baseline of line three.
            cap_px = 2 * lead + 0.77 * body
            cap_size = cap_px / 0.625
            cap_w = typeset.measure(para[0], DISPLAY, cap_size)
            sh.text(para[0], DISPLAY, cap_size, x - cap_size * 0.02, y + 2 * lead, sh.structure)
            indent = cap_w + body * 0.45
            lines = _wrap_varying(para[1:].split(), READING, body,
                                  lambda n: width - indent if n < 3 else width)
            for n, line in enumerate(lines):
                sh.text(line, READING, body, x + (indent if n < 3 else 0), y, sh.ink)
                y += lead
        else:
            y += lead * 0.45
            for line in typeset.wrap(para, READING, body, width):
                sh.text(line, READING, body, x, y, sh.ink)
                y += lead
    return y - lead


def build(L, ink, structure):
    sh = Sheet(ink, structure)
    W, pad, top, f, fl = L["W"], L["pad"], L["top"], L["fact"], L["fact_lead"]

    if L["panel"]:
        # Ruled panel on the left, every fact in its own cell.
        px0, px1 = pad, pad + L["panel"]
        cells = [[(NAME, FACT_BOLD, sh.ink)],
                 [(r, FACT, sh.ink) for r in ROLES],
                 [(PLACE, FACT, sh.ink)],
                 [(DAY_LABEL, FACT, sh.structure), (DAY, FACT, sh.ink)]]
        y = top
        sh.rule(px0, y, px1, y, sh.ink)
        for cell in cells:
            y += 7
            for text, face, colour in cell:
                y += fl
                sh.text(text, face, f, px0, y - 5, colour, TRACK)
            y += 9
            sh.rule(px0, y, px1, y, sh.ink)
        panel_bottom = y
        rx = px1 + L["gutter"]
        cx = rx + L["gutter"]
        width = W - pad - cx
        y = top + L["head"] * 0.72
        y = headline(sh, cx, y, width, L["head"])
        y = prose(sh, L, cx, y + L["head"] * 0.86, width)
        bottom = max(y + L["lead"] * 0.4, panel_bottom)
        sh.rule(rx, top, rx, bottom, sh.structure, 1)
        H = bottom + top
    else:
        # Narrow: the panel becomes ruled strips across the top.
        x0, x1 = pad, W - pad
        y = top
        sh.rule(x0, y, x1, y, sh.ink)
        y += 7 + fl
        sh.text(NAME, FACT_BOLD, f, x0, y - 5, sh.ink, TRACK)
        sh.text(PLACE, FACT, f, x1, y - 5, sh.ink, TRACK, anchor="end")
        y += 9
        sh.rule(x0, y, x1, y, sh.ink)
        y += 7
        for line in typeset.wrap(" · ".join(ROLES), FACT, f, x1 - x0, TRACK):
            y += fl
            sh.text(line, FACT, f, x0, y - 5, sh.ink, TRACK)
        y += 9
        sh.rule(x0, y, x1, y, sh.ink)
        y += 7 + fl
        w = sh.text(DAY_LABEL, FACT, f, x0, y - 5, sh.structure, TRACK)
        sh.text(DAY, FACT, f, x0 + w + f * 0.8, y - 5, sh.ink, TRACK)
        y += 9
        sh.rule(x0, y, x1, y, sh.structure, 1)
        y += 18 + L["head"] * 0.72
        y = headline(sh, x0, y, x1 - x0, L["head"])
        y = prose(sh, L, x0, y + L["head"] * 0.86, x1 - x0)
        H = y + top

    kdefs, sh.under = kaleidoscope(W, H, W * (0.62 if L["panel"] else 0.5), H * 0.5)
    sh.defs.insert(0, kdefs)
    alt = " ".join([HEADLINE, DECK] + BODY + [
        "Nihan Bayrak. AI specialist, product manager, solutions engineer. Berlin. "
        "By day, WIN Creating Images."])
    return sh.svg(W, H, alt, style=STYLE + KALEIDOSCOPE_STYLE)
