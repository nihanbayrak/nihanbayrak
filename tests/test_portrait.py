import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, "tools")
import portrait  # noqa: E402

REFERENCE = "docs/superpowers/specs/2026-11-22-living-card/portrait-reference.json"
PHOTO = Path("/private/tmp/claude-501/-Users-nihanbayrak-claude-workspace/1673e4f1-5687-4e62-9ac9-ba60e37cfe8e/scratchpad/mock/photo_from_chat_8.jpg")


class Grid(unittest.TestCase):
    def test_reference_grid_is_the_portrait(self):
        ref = json.loads(Path(REFERENCE).read_text())
        data = json.loads(Path("data/portrait.json").read_text())
        self.assertEqual((data["rows"], data["cols"]), (42, 66))
        self.assertEqual(data["grid"], ref["grid"])

    def test_background_is_zero_and_range_is_unit(self):
        photo = Image.new("RGB", (400, 400), (200, 150, 120))
        mask = Image.new("L", (400, 400), 0)
        ImageDraw.Draw(mask).ellipse((100, 50, 300, 350), fill=255)
        g = portrait.brightness(photo, mask, (0, 0, 400, 400), cols=20, rows=20)
        self.assertEqual(g[0][0], 0.0)
        self.assertTrue(all(0.0 <= v <= 1.0 for row in g for v in row))

    @unittest.skipUnless(PHOTO.exists(), "22 Nov photo not on this Mac")
    def test_photo_reproduces_reference(self):
        photo = Image.open(PHOTO).convert("RGB")
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp) / "photo.png", Path(tmp) / "mask.png"
            photo.save(src)
            subprocess.run(["swift", "tools/segment.swift", str(src), str(out)], check=True, capture_output=True)
            mask = Image.open(out).convert("L").resize(photo.size)
        g = portrait.brightness(photo, mask, (300, 120, 1150, 970), cols=66, rows=42)
        ref = json.loads(Path(REFERENCE).read_text())["grid"]
        # The reference was made with Pillow 10.4 and matches it exactly; Pillow 12's
        # resampling moves a handful of cells by up to 0.03. Same face, a sign or two apart.
        diffs = [abs(a - b) for ra, rb in zip(g, ref) for a, b in zip(ra, rb)]
        self.assertLessEqual(max(diffs), 0.05)
        self.assertGreaterEqual(sum(d <= 0.011 for d in diffs) / len(diffs), 0.99)


if __name__ == "__main__":
    unittest.main()
