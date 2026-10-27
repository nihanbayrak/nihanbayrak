"""The octopus on its own, for use away from the README.

Same renderer the profile uses, so what comes out is the same object — just with
no page around it. Stills are transparent PNGs; the turn is an animated WebP.

    python tools/export-object.py             # a still and the turn, into ~/Downloads
    python tools/export-object.py 0 12 24     # those frames of the forty-eight
    python tools/export-object.py --px 3000   # bigger
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import shade

ROOT = Path(__file__).resolve().parent.parent
FRAMES = 48


def _still(sh, i):
    rgb, a = sh.frame(math.tau * i / sh.frames, background=False)
    rgba = (np.concatenate([rgb, a[..., None]], axis=2) * 255 + 0.5).astype(np.uint8)
    im = Image.fromarray(rgba, mode="RGBA")
    box = im.getchannel("A").getbbox()          # trim to the ink, shadow included
    return im.crop(box) if box else im


def main():
    args = sys.argv[1:]
    px = 1400
    if "--px" in args:
        px = int(args[args.index("--px") + 1])
        del args[args.index("--px"):args.index("--px") + 2]
    frames = [int(a) for a in args if a.isdigit()] or [12]

    out = Path.home() / "Downloads"
    # The canvas is sized so the object lands at roughly `px` across; the shadow
    # needs the extra room underneath, which is why the box is not the canvas.
    scale = px / 460
    canvas = (round(520 * scale), round(565 * scale))
    box = (32 * scale, 20 * scale, 456 * scale, 410 * scale)
    sh = shade.Shader(ROOT / "data" / "nautilia-octopus.obj",
                      ROOT / "data" / "materials.json",
                      box=box, canvas=canvas, frames=FRAMES)
    print(f"  rendering at {canvas[0]}x{canvas[1]}")

    for i in frames:
        p = out / f"octopus-{i:02d}.png"
        im = _still(sh, i)
        im.save(p)
        print(f"  {p.name:22} {im.width}x{im.height}  {p.stat().st_size/1024:7.1f} KB")

    turn = out / "octopus-turning.webp"
    shade.turntable(sh, turn, duration=100)
    print(f"  {turn.name:22} {FRAMES} frames  {turn.stat().st_size/1024:7.1f} KB")


if __name__ == "__main__":
    main()
