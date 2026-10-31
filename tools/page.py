"""The whole page as one image on one ground: no gaps.

GitHub puts space between any two images in a README, so a page that has to read
as one surface has to be one image. This stacks every piece on a single Klein
blue ground: the octopus swimming (its frames carried inside as WebP stills and
shown one at a time), the introduction with the kaleidoscope behind it, the year
the small octopus eats, and the three cards. Each piece is still built by its own
module; this nests them, makes their glyph ids unique, and adds the octopus.

The cards stop being separate links, because one image is one click. The case
files under the image carry the links instead.

    python tools/page.py     # writes assets/page.svg and assets/page-narrow.svg

Needs fonttools and uharfbuzz. Reads data/contributions.json and the frames in
assets/octopus/ (render.py).
"""
import base64
import json
import re

import cards
import commits
import dance
import typeset
from dance import ASSETS, DISPLAY, FACT_BOLD, GROUND, THEMES, TRACK, Sheet

FRAMES_DIR = ASSETS / "octopus"
OCTO_ASPECT = 470 / 800                  # render.py's canvas
MS = 100                                 # per frame, as rendered

WIDTHS = {"wide": 800, "narrow": 380}
PALETTE = THEMES["klein"]


def octopus(W):
    """The swim, as frames shown one at a time. Returns (markup, height, style)."""
    frames = sorted(FRAMES_DIR.glob("f*.webp"))
    n, h = len(frames), round(W * OCTO_ASPECT)
    T = n * MS / 1000
    images = []
    for i, f in enumerate(frames):
        data = base64.b64encode(f.read_bytes()).decode()
        first = " f0" if i == 0 else ""
        images.append(f'<image class="f{first}" style="animation-delay:{i * MS / 1000 - T:.2f}s" '
                      f'width="{W}" height="{h}" xlink:href="data:image/webp;base64,{data}"/>')
    style = f"""
.f {{ animation: frame {T:.2f}s steps(1, end) infinite; }}
@keyframes frame {{ 0% {{ visibility: visible; }} {100 / n:.3f}%, 100% {{ visibility: hidden; }} }}
@media (prefers-reduced-motion: reduce) {{ .f {{ animation: none; visibility: hidden; }} .f0 {{ visibility: visible; }} }}
"""
    return "".join(images), h, style


def header(W, cut):
    """'Pick a card' over the three cards, set like the sheet's panel."""
    sh = Sheet(**PALETTE)
    pad = 44 if cut == "wide" else 22
    y = 30
    sh.rule(pad, y, W - pad, y, sh.ink)
    sh.text("PICK A CARD", FACT_BOLD, 11.5, pad, y + 24, sh.structure, TRACK)
    size = 22 if cut == "wide" else 19
    yy = y + 24 + size * 1.5
    for line in typeset.wrap("Three jobs, one person. Each case file under the page holds the proof.",
                             DISPLAY, size, W - 2 * pad):
        sh.text(line, DISPLAY, size, pad, yy, sh.ink)
        yy += size * 1.3
    H = round(yy)
    return sh.svg(W, H, "Pick a card. Three jobs, one person.", title="Pick a card", style="")


def nest(svg, prefix, y):
    """A piece's SVG placed at y inside the page, its glyph ids made its own."""
    svg = re.sub(r'id="(g\d+)"', rf'id="{prefix}\1"', svg)
    svg = re.sub(r'href="#(g\d+)"', rf'href="#{prefix}\1"', svg)
    H = round(float(re.search(r'<svg[^>]* height="([\d.]+)"', svg).group(1)))
    svg = re.sub(r'^<svg xmlns="[^"]+" xmlns:xlink="[^"]+" ', f'<svg x="0" y="{y}" ', svg, count=1)
    return svg, H


def build(cut):
    W = WIDTHS[cut]
    cal = json.loads(commits.DATA.read_text())
    pieces = [
        ("i", dance.build(dance.LAYOUTS[cut], **PALETTE)),
        ("y", commits.build(cal, commits.LAYOUTS[cut], **PALETTE)),
        ("h", header(W, cut)),
    ]
    for i, card in enumerate(cards.CARDS, 1):
        pieces.append((f"c{i}", cards.build(card, cards.LAYOUTS[cut], delay=.8 + i * .5, **PALETTE)))

    octo, y, octo_style = octopus(W)
    body = [f'<g>{octo}</g>']
    for prefix, svg in pieces:
        nested, h = nest(svg, prefix, y)
        body.append(nested)
        y += h
    H = y + 24

    alt = ("A brass and bone enamel octopus automaton swims on Yves Klein blue, its arms waving. "
           + " ".join([dance.HEADLINE, dance.DECK] + dance.BODY)
           + f" Nihan Bayrak: AI specialist, product manager, solutions engineer, Berlin. "
           f"Below, a year of contributions, {cal['total']} in all, as dots that a small octopus "
           "walks through and eats. Then three cards: Roundtrip, Conscious Eyes, and Brief to Concept.")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{alt}">'
            f'<title>Nihan Bayrak</title><style>{octo_style}</style>'
            f'<rect width="{W}" height="{H}" fill="{GROUND}"/>{"".join(body)}</svg>')


def main():
    for cut in WIDTHS:
        out = ASSETS / ("page" + ("-narrow" if cut == "narrow" else "") + ".svg")
        out.write_text(build(cut))
        print(f"  {out.name}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
