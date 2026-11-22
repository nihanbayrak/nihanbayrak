import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "tools")
import motion  # noqa: E402
import typeset  # noqa: E402

GRID = json.loads(Path("data/portrait.json").read_text())["grid"]
MOTTOS = ["Engineering with an editor's eye.",
          "I speak Python, fashion and three human languages.",
          "Where the model meets the moodboard."]


def edges_for(text):
    adv = typeset.advances(text, "voice", 19)
    return [0] + [a + 1.5 for a in adv], adv[-1] + 2


class Flipbook(unittest.TestCase):
    def test_exactly_one_frame_at_every_moment(self):
        css = motion.flip_css("c")
        for i in range(8000):
            self.assertEqual(len(motion.visible_frames(css, i / 8000)), 1, i)

    def test_frames_deterministic_and_glitch_only_on_3_and_6(self):
        a, b = motion.frames(GRID), motion.frames(GRID)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 8)
        self.assertEqual(len(a[0]), 42)
        self.assertEqual(len(a[0][0]), 66)
        for k in (0, 1, 2, 4, 5, 7):
            for r in range(42):
                for c in range(66):
                    if GRID[r][c] == 0:
                        self.assertEqual(a[k][r][c], " ", (k, r, c))
        for k in (3, 6):
            # a sign landing where she isn't can only come from the band sliding sideways
            moved = [r for r in range(42) if any(GRID[r][c] == 0 and a[k][r][c] != " " for c in range(66))]
            self.assertTrue(moved, k)
            self.assertLessEqual(moved[-1] - moved[0], 2, (k, moved))

    def test_signs_come_from_the_ramp(self):
        self.assertEqual(motion.RAMP, " .,:;i1tfLCG08@")
        for frame in motion.frames(GRID):
            self.assertTrue(set("".join(frame)) <= set(motion.RAMP))


class Typing(unittest.TestCase):
    def test_typing_steps_land_on_letter_edges(self):
        edges, width = edges_for(MOTTOS[0])
        css = motion.type_css("c", 0, edges, width)
        # scales are written to 4 decimals, so an edge lands within ~0.015 px of a letter's
        seen = sorted({motion.mask_scale(css, 0, p / 10000) * width for p in range(0, 1201)})
        self.assertEqual(len(seen), len(edges))
        for s, e in zip(seen, sorted(edges)):
            self.assertAlmostEqual(s, e, delta=0.05)
        self.assertAlmostEqual(motion.mask_scale(css, 0, 0.20) * width, edges[-1], delta=0.05)
        self.assertEqual(motion.mask_scale(css, 0, 0.50), 0.0)

    def test_one_motto_at_a_time(self):
        css = "".join(motion.type_css("c", j, *edges_for(m)) for j, m in enumerate(MOTTOS))
        for step in range(1800):
            t = step / 100                                   # seconds into the 18 s loop
            on = [j for j in range(3)
                  if motion.mask_scale(css, j, ((t + 18 - 6 * j) % 18) / 18) > 0]
            self.assertLessEqual(len(on), 1, (t, on))

    def test_each_motto_gets_its_turn(self):
        css = "".join(motion.type_css("c", j, *edges_for(m)) for j, m in enumerate(MOTTOS))
        for j in range(3):
            t = 6 * j + 3.6                                  # 20% into line j's own loop
            edges, width = edges_for(MOTTOS[j])
            self.assertAlmostEqual(motion.mask_scale(css, j, ((t + 18 - 6 * j) % 18) / 18), edges[-1] / width, places=3)

    def test_delays_stagger_by_six_seconds(self):
        for j in range(3):
            self.assertIn(f"{-18 + 6 * j}s infinite", motion.type_css("c", j, *edges_for(MOTTOS[j])))


class Still(unittest.TestCase):
    def test_still_css_shows_frame_0_and_line_0(self):
        css = motion.still_css("c")
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn(".cf0", css)
        self.assertIn(".cv0", css)


if __name__ == "__main__":
    unittest.main()
