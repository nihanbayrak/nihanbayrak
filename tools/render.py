"""Renders the octopus, swimming, on no ground at all.

Since 1 Nov the page is only the octopus and two words under it. The mesh is bent
each frame (swim.py) so the arms wave and the body rides each stroke, and lit by
shade.py with a transparent ground: the shadow rides in the alpha, so the animal
swims on whatever GitHub's page is, light or dark. Written as one animated WebP.

Deterministic: nothing here reads the GitHub API.
"""
from pathlib import Path

import numpy as np
from PIL import Image

import shade
import swim

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "octopus.webp"
DATA = ROOT / "data"

CANVAS = (900, 460)
BOX = (230, 34, 440, 400)    # x, y, w, h of the animal, centred; the shadow falls left,
                             # into the room the centring leaves on that side
FRAMES = 40                  # at MS each: one loop, two strokes
MS = 100
SCALE = 1.25                 # rendered above display size for retina


def main():
    w, h = CANVAS
    sh = shade.Shader(DATA / "nautilia-octopus.obj", DATA / "materials.json",
                      box=tuple(v * SCALE for v in BOX),
                      canvas=(round(w * SCALE), round(h * SCALE)), frames=48)
    frames = []
    for rgb, a in swim.frames(sh, FRAMES, background=False):
        rgba = np.concatenate([rgb, a[..., None]], axis=2)
        frames.append(Image.fromarray((rgba * 255 + .5).astype(np.uint8), mode="RGBA"))
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=MS, loop=0,
                   quality=82, method=4, minimize_size=True)
    print(f"  {OUT.name}  {FRAMES} frames  {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
