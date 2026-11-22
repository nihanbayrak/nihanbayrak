import subprocess
import sys
import unittest

sys.path.insert(0, "tools")
import typeset  # noqa: E402

LINE = "Where the model meets the moodboard."


class Voice(unittest.TestCase):
    def test_voice_advances_one_per_char_and_monotonic(self):
        adv = typeset.advances(LINE, "voice", 19)
        self.assertEqual(len(adv), 36)
        self.assertTrue(all(b > a for a, b in zip(adv, adv[1:])))
        self.assertAlmostEqual(adv[-1], typeset.measure(LINE, "voice", 19), places=2)

    def test_voice_width_matches_browser(self):
        # Chrome measured 314.33 px for this line at Fraunces italic 300, 19 px.
        self.assertAlmostEqual(typeset.advances(LINE, "voice", 19)[-1], 314.33, delta=4)

    def test_fonts_are_tracked(self):
        tracked = subprocess.run(["git", "ls-files", "tools/fonts"], capture_output=True, text=True).stdout
        self.assertIn("tools/fonts/Fraunces-Italic.ttf", tracked)


if __name__ == "__main__":
    unittest.main()
