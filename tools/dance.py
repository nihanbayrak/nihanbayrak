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
from pathlib import Path

import typeset

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

GROUND, INK, STRUCTURE = "#F5F1E8", "#1A1611", "#8B2027"
UNDER_GRAIN = "#FCF8EF"                # the grain darkens by ~7 on average; this lands it
                                       # on GROUND, the same paper the octopus plate is printed on

HEADLINE = "Care is my building language."
ACCENT_WORD = "Care"
DECK = ("AI made building fast. Most people spend that speed on building more. "
        "I spend it on attention.")
BODY = [
    "The hours AI gives back, I put into planning: what we are making, why, and how we "
    "will know it worked. Then I track it, measure it and improve it. When the numbers "
    "say the system is wrong, I take the whole thing apart and rethink it, even when "
    "that is the uncomfortable thing to do. Especially then.",
    "I trust my taste, and I test it. Most people in this field have no visual "
    "vocabulary; most people with one cannot ship. I work in between.",
]
NAME, PLACE = "NIHAN BAYRAK", "BERLIN"
ROLES = ["AI SPECIALIST", "PRODUCT MANAGER", "SOLUTIONS ENGINEER"]
DAY_LABEL, DAY = "BY DAY", "WIN CREATING IMAGES"

DISPLAY, READING, FACT, FACT_BOLD = "display", "body", "fact", "fact_bold"
TRACK = 0.1                            # small caps get air; body never does

LAYOUTS = {
    "wide": dict(W=800, pad=52, panel=164, gutter=24, head=60, deck=23, deck_lead=31,
                 body=15.5, lead=26, fact=11.5, fact_lead=18),
    "narrow": dict(W=380, pad=24, panel=None, gutter=0, head=46, deck=20, deck_lead=27,
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

GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="7" stitchTiles="stitch"/>'
         '<feColorMatrix values="0 0 0 0 .10  0 0 0 0 .086  0 0 0 0 .067  .22 0 0 0 -.07"/></filter>')


class Sheet:
    """Outlines placed on a page. Every glyph is drawn once and reused."""

    def __init__(self):
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
                f'<title>{title}</title><style>{style}</style><defs>{GRAIN}{"".join(self.defs)}</defs>'
                f'<rect width="{W}" height="{H:.0f}" fill="{UNDER_GRAIN}"/>'
                f'<rect width="{W}" height="{H:.0f}" filter="url(#grain)"/>'
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
                fill = STRUCTURE if letter < len(ACCENT_WORD) else INK
                side = " r" if letter % 2 else ""
                sh.marks.append(f'<g class="t{side}" fill="{fill}" '
                                f'style="animation-delay:{.3 + letter * STEP:.2f}s">{drawn[i]}</g>')
            letter += 1
        y += size * 1.0
    return y - size * 1.0


def prose(sh, L, x, y, width):
    """Deck, then body with a drop cap. Returns the last baseline."""
    for line in typeset.wrap(DECK, DISPLAY, L["deck"], width):
        sh.text(line, DISPLAY, L["deck"], x, y, INK)
        y += L["deck_lead"]
    y += L["lead"] * 0.55

    body, lead = L["body"], L["lead"]
    for p, para in enumerate(BODY):
        if p == 0:
            # Drop cap: from the cap height of line one to the baseline of line three.
            cap_px = 2 * lead + 0.77 * body
            cap_size = cap_px / 0.625
            cap_w = typeset.measure(para[0], DISPLAY, cap_size)
            sh.text(para[0], DISPLAY, cap_size, x - cap_size * 0.02, y + 2 * lead, STRUCTURE)
            indent = cap_w + body * 0.45
            lines = _wrap_varying(para[1:].split(), READING, body,
                                  lambda n: width - indent if n < 3 else width)
            for n, line in enumerate(lines):
                sh.text(line, READING, body, x + (indent if n < 3 else 0), y, INK)
                y += lead
        else:
            y += lead * 0.45
            for line in typeset.wrap(para, READING, body, width):
                sh.text(line, READING, body, x, y, INK)
                y += lead
    return y - lead


def build(L):
    sh = Sheet()
    W, pad, f, fl = L["W"], L["pad"], L["fact"], L["fact_lead"]

    if L["panel"]:
        # Ruled panel on the left, every fact in its own cell.
        px0, px1 = pad, pad + L["panel"]
        cells = [[(NAME, FACT_BOLD, INK)],
                 [(r, FACT, INK) for r in ROLES],
                 [(PLACE, FACT, INK)],
                 [(DAY_LABEL, FACT, STRUCTURE), (DAY, FACT, INK)]]
        y = pad
        sh.rule(px0, y, px1, y, INK)
        for cell in cells:
            y += 7
            for text, face, colour in cell:
                y += fl
                sh.text(text, face, f, px0, y - 5, colour, TRACK)
            y += 9
            sh.rule(px0, y, px1, y, INK)
        panel_bottom = y
        rx = px1 + L["gutter"]
        cx = rx + L["gutter"]
        width = W - pad - cx
        y = pad + L["head"] * 0.72
        y = headline(sh, cx, y, width, L["head"])
        y = prose(sh, L, cx, y + L["head"] * 0.86, width)
        bottom = max(y + L["lead"] * 0.4, panel_bottom)
        sh.rule(rx, pad, rx, bottom, STRUCTURE, 1)
        H = bottom + pad
    else:
        # Narrow: the panel becomes ruled strips across the top.
        x0, x1 = pad, W - pad
        y = pad
        sh.rule(x0, y, x1, y, INK)
        y += 7 + fl
        sh.text(NAME, FACT_BOLD, f, x0, y - 5, INK, TRACK)
        sh.text(PLACE, FACT, f, x1, y - 5, INK, TRACK, anchor="end")
        y += 9
        sh.rule(x0, y, x1, y, INK)
        y += 7
        for line in typeset.wrap(" · ".join(ROLES), FACT, f, x1 - x0, TRACK):
            y += fl
            sh.text(line, FACT, f, x0, y - 5, INK, TRACK)
        y += 9
        sh.rule(x0, y, x1, y, INK)
        y += 7 + fl
        w = sh.text(DAY_LABEL, FACT, f, x0, y - 5, STRUCTURE, TRACK)
        sh.text(DAY, FACT, f, x0 + w + f * 0.8, y - 5, INK, TRACK)
        y += 9
        sh.rule(x0, y, x1, y, STRUCTURE, 1)
        y += 18 + L["head"] * 0.72
        y = headline(sh, x0, y, x1 - x0, L["head"])
        y = prose(sh, L, x0, y + L["head"] * 0.86, x1 - x0)
        H = y + pad

    alt = " ".join([HEADLINE, DECK] + BODY + [
        "Nihan Bayrak. AI specialist, product manager, solutions engineer. Berlin. "
        "By day, WIN Creating Images."])
    return sh.svg(W, H, alt)


def main():
    ASSETS.mkdir(exist_ok=True)
    for cut, layout in LAYOUTS.items():
        out = ASSETS / ("intro.svg" if cut == "wide" else "intro-narrow.svg")
        out.write_text(build(layout))
        print(f"  {out.name}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
