import subprocess
import sys
import unittest
from datetime import date

sys.path.insert(0, "tools")
import neofetch  # noqa: E402

STATS = {"created": "2017-09-26", "repos": 17, "contributed": 1, "stars": 2, "followers": 28,
         "commits": 441, "added": 57126, "deleted": 14744}
DAY = date(2026, 11, 22)


class Readout(unittest.TestCase):
    def test_readout_copy(self):
        self.assertEqual(neofetch.readout(STATS, DAY), [
            ("title", "nihan@bayrak"),
            ("pair", "Based", "Berlin · TR, EN, DE"),
            ("pair", "Uptime", "9 years, 1 month, 27 days"),
            ("pair", "Kernel", "Evals, agents, honest interfaces"),
            ("pair", "Shell", "Claude Code, zsh"),
            ("blank",),
            ("section", "Now"),
            ("pair", "Measuring", "Can an LLM judge copyright risk?"),
            ("pair", "Designing", "Conscious Eyes: the label, at a glance"),
            ("pair", "Guarding", "Prompt-injection scans for chat logs"),
            ("blank",),
            ("section", "GitHub"),
            ("pair", "Commits", "441 · Repos 17 · Followers 28"),
        ])

    def test_big_numbers_and_long_uptime_fit(self):
        big = dict(STATS, commits=123456, repos=999, followers=99999)
        rows = neofetch.readout(big, date(2027, 9, 25)) + [("pair", "Uptime", "10 years, 11 months, 30 days")]
        for row in rows:
            if row[0] == "pair":
                self.assertLessEqual(len(row[1]) + 1 + (12 - len(row[1])) + 1 + len(row[2]), 52, row)


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
        self.assertLess(24 + neofetch.Mono().width(neofetch.INFO_COLS, neofetch.INFO_SIZE), 470)
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
