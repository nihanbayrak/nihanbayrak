"""The moving introduction: "Care is my building language." and the paragraphs under it.

A README allows no script, and pointer events never reach an image, so hover is
out. What survives is CSS animation inside the image itself. Three things move:

  rise   once, on load: every word comes up out of the line in reading order
  hop    the headline, letter by letter: a wave with a bounce and a squash
  bob    the paragraphs, word by word: a small ripple that follows the headline
         across the block, so the text stays readable while it moves

All three share one cycle, so the ripple always arrives just after the hop.
Anyone who has asked their system for reduced motion gets the text standing
still, and a renderer that ignores CSS animation shows it still and complete.

The type has to be outlines (see typeset.py). Each glyph is drawn once in <defs>
and placed with <use>, which keeps a page of text to tens of kilobytes. GitHub
picks the file through <picture>: two themes, and a narrow cut for phones, where
the wide one would shrink the text below reading size.

Needs fonttools and uharfbuzz, which the workflow does not install, so the
Action never calls this. Run it by hand and commit the four SVGs. The README's
alt text repeats this copy; change both together.
"""
from pathlib import Path

import typeset

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

HEADLINE = "Care is my building language."
ACCENT_WORD = "Care"                  # one accent per piece
PARAGRAPHS = [
    "AI made building fast. Most people spend that speed on building more. "
    "I spend it on attention.",
    "The hours AI gives back, I put into planning: what we are making, why, and how "
    "we will know it worked. Then I track it, measure it and improve it. When the "
    "numbers say the system is wrong, I take the whole thing apart and rethink it, "
    "even when that is the uncomfortable thing to do. Especially then.",
    "I trust my taste, and I test it. Most people in this field have no visual "
    "vocabulary; most people with one cannot ship. I work in between.",
    "By day I build AI systems at WIN Creating Images, a creative packaging agency "
    "in Berlin.",
]

FACE = "display_med"                  # Cormorant Infant 500, headline and body alike

LAYOUTS = {
    # canvas width, headline size, body size, body column, line height, paragraph gap
    "wide": dict(width=800, head=58, body=23, column=640, leading=34, gap=14),
    "narrow": dict(width=380, head=44, body=21, column=340, leading=30, gap=12),
}

THEMES = {
    "light": {"ink": "#1A1611", "accent": "#8B2027"},
    "dark": {"ink": "#F0EBE0", "accent": "#D25C64"},
}

CYCLE = 4.0                           # seconds between waves
SETTLE = 1.4                          # the first wave waits for the entrance

STYLE = f"""
.w {{ transform-box: fill-box; animation: rise .6s cubic-bezier(.2,.7,.2,1) backwards; }}
.l, .b {{ transform-box: fill-box; transform-origin: 50% 100%;
          animation: hop {CYCLE}s cubic-bezier(.3,.7,.4,1) infinite backwards; }}
.l.r {{ animation-name: hop-r; }}
.b {{ animation-name: bob; animation-timing-function: ease-in-out; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes hop {{
  0%, 13%, 100% {{ transform: none; }}
  4%  {{ transform: translateY(-24px) rotate(-8deg) scale(1.04, 1.07); }}
  8%  {{ transform: translateY(3px) rotate(2deg) scale(1.07, .92); }}
}}
@keyframes hop-r {{
  0%, 13%, 100% {{ transform: none; }}
  4%  {{ transform: translateY(-24px) rotate(8deg) scale(1.04, 1.07); }}
  8%  {{ transform: translateY(3px) rotate(-2deg) scale(1.07, .92); }}
}}
@keyframes bob {{
  0%, 12%, 100% {{ transform: none; }}
  5%  {{ transform: translateY(-5px) rotate(-1.5deg); }}
  9%  {{ transform: translateY(1px); }}
}}
@media (prefers-reduced-motion: reduce) {{ .w, .l, .b {{ animation: none; }} }}
"""


class Glyphs:
    """Every glyph outline once, in <defs>, keyed by glyph name."""

    def __init__(self):
        _, self.glyphset, _, self.upem = typeset._load(FACE)
        self.ids, self.defs = {}, []

    def ref(self, name):
        if name not in self.ids:
            pen = typeset.SVGPathPen(self.glyphset, ntos=lambda v: str(int(round(v))))
            self.glyphset[name].draw(pen)
            d = pen.getCommands()
            self.ids[name] = f"g{len(self.ids)}" if d else None
            if d:
                self.defs.append(f'<path id="{self.ids[name]}" d="{d}"/>')
        return self.ids[name]

    def use(self, name, x, y, size):
        gid = self.ref(name)
        if gid is None:
            return ""
        s = size / self.upem
        return f'<use xlink:href="#{gid}" transform="translate({x:.2f} {y:.2f}) scale({s:.5f} {-s:.5f})"/>'


def _width(text, size):
    return typeset.measure(text, FACE, size)


def build(layout, ink, accent):
    W, head, body = layout["width"], layout["head"], layout["body"]
    column, leading, gap = layout["column"], layout["leading"], layout["gap"]
    gl = Glyphs()
    out = []

    # ---- headline, centred, letter by letter
    head_lines = typeset.wrap(HEADLINE, FACE, head, W - 32)
    y = head * 1.05
    letter = 0
    for line in head_lines:
        placed, adv = typeset.shape(line, FACE)
        x0 = (W - adv * head / gl.upem) / 2
        for name, gx in placed:
            glyph = gl.use(name, x0 + gx * head / gl.upem, y, head)
            if glyph:
                fill = accent if letter < len(ACCENT_WORD) and HEADLINE.startswith(ACCENT_WORD) else ink
                side = " r" if letter % 2 else ""
                out.append(
                    f'<g class="w" style="animation-delay:{letter * .02:.3f}s">'
                    f'<g class="l{side}" fill="{fill}" style="animation-delay:{SETTLE + letter * .045:.3f}s">'
                    f'{glyph}</g></g>')
            letter += 1
        y += head * 1.08
    y += head * 0.35

    # ---- paragraphs, word by word, left aligned in a centred column
    left = (W - column) / 2
    space = _width(" ", body)
    ripple_start = SETTLE + letter * .045 * .6
    word_index, line_index = 0, 0
    for para in PARAGRAPHS:
        for line in typeset.wrap(para, FACE, body, column):
            x = left
            for word in line.split(" "):
                placed, adv = typeset.shape(word, FACE)
                glyphs = "".join(gl.use(n, x + gx * body / gl.upem, y, body) for n, gx in placed)
                sweep = (x - left) / column
                out.append(
                    f'<g class="w" style="animation-delay:{.2 + word_index * .007:.3f}s">'
                    f'<g class="b" fill="{ink}" style="animation-delay:'
                    f'{ripple_start + sweep * .7 + line_index * .07:.3f}s">{glyphs}</g></g>')
                x += adv * body / gl.upem + space
                word_index += 1
            y += leading
            line_index += 1
        y += gap
    H = y - gap - leading + body * 0.6

    alt = " ".join([HEADLINE] + PARAGRAPHS)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img" aria-label="{alt}">'
            f'<title>{HEADLINE}</title><style>{STYLE}</style>'
            f'<defs>{"".join(gl.defs)}</defs>{"".join(out)}</svg>')


def main():
    ASSETS.mkdir(exist_ok=True)
    for theme, colours in THEMES.items():
        for cut, layout in LAYOUTS.items():
            name = f"intro-{theme}" + ("-narrow" if cut == "narrow" else "")
            out = ASSETS / f"{name}.svg"
            out.write_text(build(layout, **colours))
            print(f"  {out.name}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
