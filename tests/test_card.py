import subprocess
import sys
import unittest
from datetime import date

sys.path.insert(0, "tools")
import neofetch  # noqa: E402

STATS = {"created": "2017-09-26", "repos": 17, "contributed": 1, "stars": 2, "followers": 28,
         "commits": 441, "added": 57126, "deleted": 14744}
DAY = date(2026, 11, 22)


TEXT = """nihan: Profile

role: AI specialist
dayJob: AI tools for consumer brands
city: Berlin
spokenLanguages: TR, EN, DE

tools.languages: Python, TypeScript, SQL
tools.ide: Claude Code, Xcode, Codex, VS Code, Langdock
tools.shell: zsh

interests.creative: 3D modeling and printing
interests.offScreen: Modeling, sailing, creating gifts

building: Projects

evals: Copyright risk in image prompts
agents: Roundtrip · TestFlight feedback triage
product: Conscious Eyes · iOS label scanner

contact: Contact

linkedIn: nihan-bayrak
website: consciouseyes.app"""


class Readout(unittest.TestCase):
    def test_the_card_says_exactly_my_text(self):
        # Written by me, 22 Nov. Line for line, no leaders, no rules, no live lines.
        rendered = "\n".join("".join(t for t, _ in neofetch.spans(line)) for line in neofetch.readout())
        self.assertEqual(rendered, TEXT)

    def test_every_line_fits(self):
        for line in neofetch.readout():
            self.assertLessEqual(sum(len(t) for t, _ in neofetch.spans(line)), neofetch.INFO_COLS, line)

    def test_readout_fits_left_of_the_portrait(self):
        self.assertLessEqual(24 + neofetch.Mono().width(neofetch.INFO_COLS, neofetch.INFO_SIZE), 462)


class Card(unittest.TestCase):
    def test_card_rules(self):
        for stacked in (False, True):
            svg = neofetch.build(stacked, today=DAY)
            p = "n" if stacked else "c"
            self.assertNotIn("<text", svg)
            self.assertNotIn("@font-face", svg)
            self.assertLess(len(svg.encode()), 1_000_000)
            for k in range(8):
                self.assertIn(f'class="{p}f{k}"', svg)
            for j in range(3):
                self.assertIn(f'class="{p}v{j}"', svg)
            self.assertIn("prefers-reduced-motion", svg)
            self.assertIn("#0B3B2E", svg)
            for banned in ("WIN", "Creating Images", "spy", "FR"):
                self.assertNotIn(banned, svg)

    def test_wide_card_is_flipped(self):
        # Readout and mottos on the left, her face on the right (Nihan's pick "B", 22 Nov).
        svg = neofetch.build(False, today=DAY)
        for there in ('translate(470.0 ', 'translate(24.0 ', 'translate(24.00 ', 'x="24"', "transform-origin:24px 0"):
            self.assertIn(there, svg)
        self.assertNotIn("translate(384.", svg)
        self.assertLess(24 + max(neofetch.typeset.measure(m, "voice", 19) for m in neofetch.MOTTOS), 470)

    def test_alt_text(self):
        self.assertIn('aria-label="Nihan Bayrak as a moving terminal readout: her portrait drawn in signs '
                      'beside her details. Berlin."', neofetch.build(False, today=DAY))

    def test_same_day_same_bytes(self):
        self.assertEqual(neofetch.build(False, today=DAY), neofetch.build(False, today=DAY))

    def test_nightly_path_needs_no_numpy_or_pillow(self):
        # The Action installs only fonttools and uharfbuzz.
        code = ("import sys; sys.modules['numpy'] = None; sys.modules['PIL'] = None; "
                "sys.path.insert(0, 'tools'); import neofetch, stats")
        self.assertEqual(subprocess.run([sys.executable, "-c", code]).returncode, 0)

    def test_readme_shows_the_living_card(self):
        with open("README.md") as f:
            readme = f.read()
        self.assertIn('srcset="assets/card-narrow.svg"', readme)
        self.assertIn('src="assets/card.svg"', readme)
        self.assertNotIn("card-light", readme)
        self.assertNotIn("WIN Creating Images", readme)


if __name__ == "__main__":
    unittest.main()
