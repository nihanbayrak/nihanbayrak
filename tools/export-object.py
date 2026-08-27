"""The octopus on its own — no card, no ground, no type, no background.

For use away from the README: a deck, a post, a print. Two forms come out of the
same geometry.

The engraving is scale-dependent on purpose: hatch spacing and stroke weights are
absolute plate units, so drawing the animal larger would print it with finer
lines relative to its body and it would stop looking like the same object. So it
is always cut at the plate's own size and then the whole drawing is scaled by the
viewBox. Identical marks, any size.

    python tools/export-object.py            # svg + png into ~/Downloads
    python tools/export-object.py 12         # one frame of the forty
    python tools/export-object.py --solid 12 # paper behind it, not see-through
"""
import math
import sys
from pathlib import Path

import engrave
import model3d

ROOT = Path(__file__).resolve().parent.parent
PLATE_W, PLATE_H = 344, 313      # the same box the README card gives it
MARGIN = 8                       # room for round line caps at the silhouette


def build(frame=None, px=2400, fill=None):
    """Standalone SVG. `frame` None means the whole turn, animated.

    `fill` lays paper inside the silhouette. Without it the animal is genuinely
    see-through — correct on the README, where the card's grain should read
    through, and a surprise anywhere the background is not plain.
    """
    v, f, accent = model3d.load_obj(ROOT / "data" / "nautilia-octopus.obj")
    plate = engrave.Engraver(v, f, accent, (0, 0, PLATE_W, PLATE_H))

    vw, vh = PLATE_W + 2 * MARGIN, PLATE_H + 2 * MARGIN
    if frame is None:
        body = f"<style>{engrave.STYLE}</style>" + plate.plate(fill)
    else:
        body = plate.frame(math.tau * frame / engrave.FRAMES, fill)

    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{-MARGIN} {-MARGIN} {vw} {vh}" '
            f'width="{px}" height="{round(px * vh / vw)}" role="img">{body}</svg>')


def main():
    out = Path.home() / "Downloads"
    args = sys.argv[1:]
    fill = "#F5F1E8" if "--solid" in args else None
    tag = "-solid" if fill else ""
    frames = [int(a) for a in args if a.lstrip("-").isdigit()] or [0, 5, 15, 25]

    turning = out / f"octopus-turning{tag}.svg"
    turning.write_text(build(fill=fill))
    print(f"  {turning.name:28} {turning.stat().st_size/1024:7.1f} KB   vector, animated")

    for i in frames:
        p = out / f"octopus-{i:02d}{tag}.svg"
        p.write_text(build(frame=i, fill=fill))
        print(f"  {p.name:28} {p.stat().st_size/1024:7.1f} KB   vector, still")


if __name__ == "__main__":
    main()
