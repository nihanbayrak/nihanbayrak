"""The line that dances: "Care is my building language."

A README allows no script, and pointer events never reach an image, so hover is
out. What survives is animation inside the image itself: every glyph is its own
outline with its own delay, and a hop runs through the line every few seconds,
then rests so it can be read. Anyone who has asked their system for reduced
motion gets the line standing still.

The type has to be outlines (see typeset.py), and GitHub picks the file per
theme through <picture>, so this writes a light and a dark version.

Needs fonttools and uharfbuzz, which the workflow does not install, so the
Action never calls this. Run it by hand and commit the two SVGs.
"""
from pathlib import Path

import typeset

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

LINE = "Care is my building language."
ACCENT_WORD = "Care"                  # one accent per piece
FACE = "display_med"                  # Cormorant Infant 500
SIZE = 64
PAD_X, PAD_TOP, PAD_BOTTOM = 24, 34, 24   # room above for the hop

CYCLE = 5.0                           # seconds; the hop takes the first ~1.6 of it
STEP = 0.055                          # delay between neighbouring letters

THEMES = {
    "light": {"ink": "#1A1611", "accent": "#8B2027"},
    "dark": {"ink": "#F0EBE0", "accent": "#D25C64"},
}

STYLE = f"""
.g {{ transform-box: fill-box; transform-origin: 50% 100%;
      animation: hop {CYCLE}s cubic-bezier(.3,.7,.4,1) infinite both; }}
.g.r {{ animation-name: hop-r; }}
@keyframes hop {{
  0%   {{ transform: none; }}
  5%   {{ transform: translateY(-16px) rotate(-6deg); }}
  10%  {{ transform: translateY(2px) rotate(2deg); }}
  14%  {{ transform: none; }}
  100% {{ transform: none; }}
}}
@keyframes hop-r {{
  0%   {{ transform: none; }}
  5%   {{ transform: translateY(-16px) rotate(6deg); }}
  10%  {{ transform: translateY(2px) rotate(-2deg); }}
  14%  {{ transform: none; }}
  100% {{ transform: none; }}
}}
@media (prefers-reduced-motion: reduce) {{ .g {{ animation: none; }} }}
"""


def build(ink, accent):
    tt, glyphset, _, upem = typeset._load(FACE)
    placed, advance = typeset.shape(LINE, FACE)
    scale = SIZE / upem
    width = advance * scale + 2 * PAD_X
    height = PAD_TOP + SIZE + PAD_BOTTOM
    baseline = PAD_TOP + SIZE * 0.78

    accent_end = len(ACCENT_WORD) if LINE.startswith(ACCENT_WORD) else 0
    letters = []
    for i, (name, x) in enumerate(placed):
        pen = typeset.SVGPathPen(glyphset, ntos=lambda v: str(int(round(v))))
        glyphset[name].draw(pen)
        d = pen.getCommands()
        if not d:                       # a space: keeps its place in the wave
            continue
        fill = accent if i < accent_end else ink
        side = " r" if i % 2 else ""
        letters.append(
            f'<g class="g{side}" style="animation-delay:{i * STEP:.3f}s" fill="{fill}">'
            f'<path transform="translate({PAD_X + x * scale:.2f} {baseline:.2f}) '
            f'scale({scale:.5f} {-scale:.5f})" d="{d}"/></g>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
            f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="{LINE}">'
            f'<title>{LINE}</title><style>{STYLE}</style>{"".join(letters)}</svg>')


def main():
    ASSETS.mkdir(exist_ok=True)
    for theme, colours in THEMES.items():
        out = ASSETS / f"care-{theme}.svg"
        out.write_text(build(**colours))
        print(f"  {out.name}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
