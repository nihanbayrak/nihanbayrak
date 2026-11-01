"""The two words under the octopus: Harness engineer.

Set in Cormorant Infant Light, the page's display face, as outlines (a README
image cannot load a font; see typeset.py). Transparent, so the ink follows
GitHub's theme: one file for light, one for dark, picked through <picture>.
"""
from pathlib import Path

import typeset

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

WORDS = "Harness engineer"
FACE, SIZE = "display", 72
INKS = {"light": "#1A1611", "dark": "#F0EBE0"}


def build(ink):
    pad = 12
    width = typeset.measure(WORDS, FACE, SIZE)
    W, H = round(width + 2 * pad), round(SIZE * 1.25)
    glyphs = typeset.text(WORDS, FACE, SIZE, pad, SIZE * 0.92, ink)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{WORDS}"><title>{WORDS}</title>{glyphs}</svg>')


def main():
    for theme, ink in INKS.items():
        out = ASSETS / f"title-{theme}.svg"
        out.write_text(build(ink))
        print(f"  {out.name}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
