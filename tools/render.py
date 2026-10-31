"""Renders the octopus, swimming, as a loop of frames for the page to carry.

It has been an engraving, then a turntable; Nihan's note on 1 Nov is that the
octopus should move for real. So the mesh is bent each frame (swim.py) and lit
by shade.py on the page's own Klein blue, with its shadow on that blue. The
frames are written as stills, not as an animated image, because the page is one
SVG with no gaps and the frames ride inside it (page.py).

Deterministic: nothing here reads the GitHub API.
"""
from pathlib import Path

import numpy as np
from PIL import Image

import shade
import swim
from dance import GROUND

ROOT = Path(__file__).resolve().parent.parent
FRAMES_DIR = ROOT / "assets" / "octopus"
DATA = ROOT / "data"

CANVAS = (800, 470)          # the top of the page, at its own width
BOX = (200, 34, 440, 400)    # x, y, w, h of the animal; the lamp is upper right, so the
                             # shadow falls left and the box sits right of centre for it
FRAMES = 40                  # at MS each: one loop, two strokes
MS = 100
SCALE = 1.25                 # rendered a little above display size for retina


def ground_rgb():
    return np.array([int(GROUND[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0


def main():
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    w, h = CANVAS
    bx, by, bw, bh = BOX
    sh = shade.Shader(DATA / "nautilia-octopus.obj", DATA / "materials.json",
                      box=tuple(v * SCALE for v in (bx, by, bw, bh)),
                      canvas=(round(w * SCALE), round(h * SCALE)), frames=48)
    sh.ground = ground_rgb()
    total = 0
    for i, (rgb, _) in enumerate(swim.frames(sh, FRAMES)):
        out = FRAMES_DIR / f"f{i:02d}.webp"
        Image.fromarray((rgb * 255 + .5).astype(np.uint8)).save(out, quality=80, method=6)
        total += out.stat().st_size
    print(f"  octopus/  {FRAMES} frames  {total / 1024:.0f} KB")


if __name__ == "__main__":
    main()
