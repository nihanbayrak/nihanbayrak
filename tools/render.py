"""Renders the profile's one visual: the octopus, turning.

It used to be an engraving — the mesh rasterised and then re-cut as hatch lines,
which kept the whole thing vector. Nihan's note on 27 Aug settles it: it has to
look like the model, and the model is a shaded object, not a drawing. So the page
gets a real render, and a real render of a smooth surface is raster. See shade.py.

Nothing here reads the GitHub API and nothing carries type any more, so the render
is deterministic and `typeset.py` is no longer in the path — it stays in the repo
because the outline trick is worth keeping if type ever returns to an image.
"""
from pathlib import Path

import shade

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"

CANVAS = (1234, 706)         # shown at 700 wide, so it stays crisp on retina
BOX = (275, 40, 684, 615)    # x, y, w, h of the object itself. The lamp is upper right,
                             # so the shadow runs ~190 px left of the box; the room on the
                             # left is for it, and as much again on the right keeps the animal
                             # centred under the name. At 520 wide it was cut off in 37 of 48 frames.
FRAMES = 48
MS = 100                     # 4.8 seconds a revolution


def main():
    ASSETS.mkdir(exist_ok=True)
    sh = shade.Shader(DATA / "nautilia-octopus.obj", DATA / "materials.json",
                      box=BOX, canvas=CANVAS, frames=FRAMES)
    out = ASSETS / "object.webp"
    n = shade.turntable(sh, out, duration=MS)
    print(f"  {out.name}  {n} frames  {out.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
