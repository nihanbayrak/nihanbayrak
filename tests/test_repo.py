import subprocess
import sys
import unittest

sys.path.insert(0, "tools")
import typeset  # noqa: E402

GONE = ["assets/object.webp", "assets/octopus.webp", "assets/title-dark.svg", "assets/title-light.svg",
        "data/materials.json", "data/nautilia-octopus.obj", "tools/render.py", "tools/swim.py",
        "tools/shade.py", "tools/model3d.py", "tools/export-object.py", "tools/title.py",
        "tools/variants.py", "tools/fonts/CormorantInfant.ttf", "tools/fonts/ArchivoNarrow.ttf"]
KEPT = ["data/profile.toml", "data/work.json", "tools/export-site-data.py"]


class Repo(unittest.TestCase):
    def test_only_the_card_remains(self):
        tracked = set(subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split())
        self.assertFalse(tracked & set(GONE))
        self.assertTrue(set(KEPT) <= tracked)
        self.assertEqual(set(typeset.FACES), {"mono", "mono_bold", "mono_light", "voice"})


if __name__ == "__main__":
    unittest.main()
