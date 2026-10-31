"""Turns a photo into the portrait on the card: signs only, no letters.

    python tools/portrait.py PHOTO [--box x0,y0,x1,y1] [--cols 46]

Writes data/portrait.txt. The photo itself never enters the repo; only the
characters do. The wall behind her is dropped by colour (hair, skin and clothes
are all more saturated than a grey wall), the face is equalised inside that mask
so its features carry, and edges are darkened so the outline reads at 46 columns.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "portrait.txt"

RAMP = " .`',:;-~+=*%#&$@"      # light to dense; signs only
CELL = 0.5                      # a monospace cell is about half as wide as it is tall


def portrait(photo, box, cols, edge=0.45, gamma=1.3):
    rgb = Image.open(photo).convert("RGB").crop(box)
    hsv = np.asarray(rgb.convert("HSV")).astype(float) / 255
    person = ((hsv[..., 1] > 0.14) | (hsv[..., 2] < 0.5)).astype(np.uint8) * 255
    mask = Image.fromarray(person).filter(ImageFilter.MedianFilter(9)).filter(ImageFilter.MaxFilter(7))
    grey = ImageOps.equalize(rgb.convert("L"), mask=mask)

    w, h = grey.size
    rows = round(cols * h / w * CELL)
    tone = np.asarray(grey.resize((cols, rows), Image.LANCZOS)).astype(float) / 255
    edges = grey.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    edge_v = np.asarray(edges.resize((cols, rows), Image.LANCZOS)).astype(float) / 255
    keep = np.asarray(mask.resize((cols, rows), Image.BILINEAR)).astype(float) / 255

    v = np.clip(tone ** gamma - edge * edge_v, 0, 1)
    idx = ((1 - v) * (len(RAMP) - 1) + .5).astype(int)
    idx[keep < 0.5] = 0
    return ["".join(RAMP[i] for i in row).rstrip() for row in idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--box", default="250,60,820,760")
    ap.add_argument("--cols", type=int, default=46)
    a = ap.parse_args()
    lines = portrait(a.photo, tuple(int(v) for v in a.box.split(",")), a.cols)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"  {OUT.name}  {len(lines)} rows x {max(map(len, lines))} cols")


if __name__ == "__main__":
    main()
