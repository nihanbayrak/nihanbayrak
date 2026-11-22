"""Turns a photo into the portrait on the card: a grid of brightness, no picture.

    python tools/portrait.py PHOTO [--box x0,y0,x1,y1]

Writes data/portrait.json, 42 rows by 66 columns, brightness 0..1 to two decimals.
The photo itself never enters the repo, and neither does its mask: both stay in a
temporary folder. Mac only — she is cut out with Apple's on-device person
segmentation (tools/segment.swift), which drops the wall and anyone behind her far
better than a colour key did. Inside that mask the face is contrast-stretched and
sharpened so the eyes, nose and lips carry at 66 columns.

The default box is the approved crop of the 22 Nov photo (1500 x 2000): face and
hair, square. It is scaled for photos of another size.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "portrait.json"
SEGMENT = Path(__file__).resolve().parent / "segment.swift"
COLS, ROWS = 66, 42
BOX = (300, 120, 1150, 970)


def brightness(photo, mask, box, cols, rows):
    """Brightness 0..1 per cell, zero outside her. `mask` is 0..255, same size as `photo`."""
    photo, mask = photo.crop(box), mask.crop(box)
    m = np.asarray(mask.resize((cols, rows), Image.BOX), dtype=float) / 255
    m = np.clip((m - 0.45) / 0.25, 0, 1)            # faint people in the background fall to 0
    grey = ImageOps.autocontrast(ImageOps.grayscale(photo), cutoff=(2, 1),
                                 mask=mask.point(lambda v: 255 if v > 140 else 0))
    grey = grey.filter(ImageFilter.UnsharpMask(8, 220, 1))
    b = (np.asarray(grey.resize((cols, rows), Image.BOX), dtype=float) / 255) ** 1.7 * m
    return [[round(float(v), 2) for v in row] for row in b]


def person_mask(photo):
    with tempfile.TemporaryDirectory() as tmp:
        src, out = Path(tmp) / "photo.png", Path(tmp) / "mask.png"
        photo.save(src)
        subprocess.run(["swift", str(SEGMENT), str(src), str(out)], check=True)
        return Image.open(out).convert("L").resize(photo.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--box", help="x0,y0,x1,y1 in the photo's pixels")
    a = ap.parse_args()
    photo = ImageOps.exif_transpose(Image.open(a.photo)).convert("RGB")
    if a.box:
        box = tuple(int(v) for v in a.box.split(","))
    else:
        sx, sy = photo.width / 1500, photo.height / 2000
        box = (round(BOX[0] * sx), round(BOX[1] * sy), round(BOX[2] * sx), round(BOX[3] * sy))
    grid = brightness(photo, person_mask(photo), box, COLS, ROWS)
    OUT.write_text(json.dumps({"rows": ROWS, "cols": COLS, "grid": grid}) + "\n")
    print(f"  {OUT.name}  {ROWS} rows x {COLS} cols")


if __name__ == "__main__":
    main()
