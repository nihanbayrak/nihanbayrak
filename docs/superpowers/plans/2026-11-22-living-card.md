# The Living Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the still, four-theme neofetch card with one moving dark-green card (plus a phone cut): her ASCII portrait as an 8-frame flipbook, a personal readout, and three typed mottos.

**Architecture:** The pipeline stays: `stats.py` → `data/stats.json`, a portrait grid in `data/`, `neofetch.py` → SVGs in `assets/`, the nightly Action redraws. New: `tools/motion.py` holds every animation rule as pure functions (frames, flip CSS, typing CSS) so they are tested without a browser; `neofetch.py` only lays out. All type is outlined by `typeset.py`, including a new Fraunces italic face.

**Tech Stack:** Python 3.12, fontTools 4.63.0 + uharfbuzz 0.56.0 (the nightly job's only packages), numpy + Pillow + Apple Vision (Mac-only portrait tool), stdlib `unittest`, Playwright with the Mac's Chrome for the playback check.

**Spec:** `docs/superpowers/specs/2026-11-22-living-card-design.md`, with its reference folder `docs/superpowers/specs/2026-11-22-living-card/`.

## Global Constraints

- Work in the worktree `~/claude_workspace/github-profile-living-card`, branch `living-card`. Never `cd` to `~/claude_workspace/github-profile`; another session uses it.
- Python: `../github-profile/.venv/bin/python` (numpy 2.5.2, pillow 12.3.0, fontTools 4.63.0, uharfbuzz 0.56.0). Tests: `../github-profile/.venv/bin/python -m unittest discover -s tests -v`. Do not install pytest or anything else.
- Colours: ground `#0B3B2E`, mid `#4FA383`, pale `#D3F2E4`. Grain: `feTurbulence` fractalNoise, baseFrequency .9, 2 octaves, opacity .08, `mix-blend-mode:screen`.
- No `<text` and no `@font-face` in any asset. All type through `tools/typeset.py`.
- Portrait ramp exactly ` .,:;i1tfLCG08@`; grid 42 rows × 66 cols; jitter ±0.09 on cells with brightness > 0.02; frames 3 and 6 shift a 3-row band by 2 or 3 columns.
- Flipbook: 8 frames, 1.6 s, `step-end`, no delay, frame k visible from `k/8` to `(k+1)/8`.
- Mottos: 18 s loop, line j delayed `-18 + 6j` s; type 0→12%, hold to 28%, erase to 32%; mask edge = glyph right edge + 1.5 px.
- Readout copy, mottos and alt text are fixed by the spec. Copy them verbatim; never reword.
- Her photo never enters git. Each card SVG under 1,000,000 bytes.
- Push only to `origin living-card`, only in Task 6. Never push `main`. Stage named paths, never `git add -A`.

## Review Focus

1. **Numbers that grow.** Commits past 9,999 or followers past 999 must still fit the 52-column readout row. Test in Task 4.
2. **The longest uptime.** "10 years, 11 months, 30 days" must fit beside its key. Test in Task 4.
3. **The nightly redraw.** Two runs on the same day must write byte-identical SVGs, or the bot commits noise every night. Test in Task 4.
4. **Safari.** The mask scaling uses `transform-box: fill-box`. Run the playback check in WebKit too if Playwright has it. Task 5.
5. **The font in CI.** If the Fraunces file is not tracked by git, the nightly job dies. Test in Task 1.

---

### Task 1: Fraunces italic in the typesetter

**Files:**
- Create: `tools/fonts/Fraunces-Italic.ttf`, `tools/fonts/Fraunces-OFL.txt`
- Modify: `tools/typeset.py` (`FACES`, `_load`, new `advances`)
- Test: `tests/test_typeset.py`

**Interfaces:**
- Produces: face name `"voice"` (Fraunces italic, wght 300, opsz 19); `typeset.advances(text: str, face: str, size: float) -> list[float]`, the right edge in px of each character of `text`, one entry per character.

- [ ] **Step 1: STOP and ask Nihan before downloading.** Name the files and source: `Fraunces-Italic[SOFT,WONK,opsz,wght].ttf` and `OFL.txt` from `https://github.com/google/fonts/tree/main/ofl/fraunces` (SIL Open Font License). Wait for her yes. Save them as `tools/fonts/Fraunces-Italic.ttf` and `tools/fonts/Fraunces-OFL.txt`.

- [ ] **Step 2: Write the failing tests** in `tests/test_typeset.py` (add `sys.path.insert(0, "tools")` at the top):

```python
def test_voice_advances_one_per_char_and_monotonic(self):
    adv = typeset.advances("Where the model meets the moodboard.", "voice", 19)
    self.assertEqual(len(adv), 36)
    self.assertTrue(all(b > a for a, b in zip(adv, adv[1:])))
    self.assertAlmostEqual(adv[-1], typeset.measure("Where the model meets the moodboard.", "voice", 19), places=2)

def test_voice_width_matches_browser(self):
    # Chrome measured 314.33 px for this line at Fraunces italic 300, 19 px.
    self.assertAlmostEqual(typeset.advances("Where the model meets the moodboard.", "voice", 19)[-1], 314.33, delta=4)

def test_fonts_are_tracked(self):
    tracked = subprocess.run(["git", "ls-files", "tools/fonts"], capture_output=True, text=True).stdout
    self.assertIn("tools/fonts/Fraunces-Italic.ttf", tracked)
```

- [ ] **Step 3: Run them to see them fail.** Run: `../github-profile/.venv/bin/python -m unittest tests.test_typeset -v`. Expected: FAIL (`KeyError: 'voice'`, no `advances`).

- [ ] **Step 4: Implement.** `FACES` values become `(filename, {axis: value})`; existing entries map weight to `{"wght": w}`; add `"voice": ("Fraunces-Italic.ttf", {"wght": 300, "opsz": 19})`. `_load` passes that dict to `instancer.instantiateVariableFont`. `advances` shapes with HarfBuzz and accumulates `x_advance` per cluster, so each character gets the right edge of the glyph that covers it.

- [ ] **Step 5: Run the tests.** Expected: 3 PASS. Then `git add tools/fonts/Fraunces-Italic.ttf tools/fonts/Fraunces-OFL.txt` (step 3's tracking test needs the files staged at least) and rerun: PASS.

- [ ] **Step 6: Commit.** `git add tools/typeset.py tests/test_typeset.py tools/fonts/Fraunces-Italic.ttf tools/fonts/Fraunces-OFL.txt && git commit -m "Fraunces italic in the typesetter, with per-letter advances"`

---

### Task 2: The portrait grid

**Files:**
- Create: `tools/segment.swift` (copy of the spec folder's), `data/portrait.json`
- Rewrite: `tools/portrait.py`
- Delete: `data/portrait.txt`
- Test: `tests/test_portrait.py`

**Interfaces:**
- Produces: `data/portrait.json` = `{"rows": 42, "cols": 66, "grid": [[float]]}`, brightness 0..1, two decimals. `portrait.brightness(photo: Image, mask: Image, box: tuple[int,int,int,int], cols: int, rows: int) -> list[list[float]]`.

- [ ] **Step 1: Write the failing tests:**

```python
def test_reference_grid_is_the_portrait(self):
    ref = json.load(open("docs/superpowers/specs/2026-11-22-living-card/portrait-reference.json"))
    data = json.load(open("data/portrait.json"))
    self.assertEqual((data["rows"], data["cols"]), (42, 66))
    self.assertEqual(data["grid"], ref["grid"])

def test_background_is_zero_and_range_is_unit(self):
    photo = Image.new("RGB", (400, 400), (200, 150, 120))
    mask = Image.new("L", (400, 400), 0); ImageDraw.Draw(mask).ellipse((100, 50, 300, 350), fill=255)
    g = portrait.brightness(photo, mask, (0, 0, 400, 400), cols=20, rows=20)
    self.assertEqual(g[0][0], 0.0)
    self.assertTrue(all(0.0 <= v <= 1.0 for row in g for v in row))

PHOTO = Path("/private/tmp/claude-501/-Users-nihanbayrak-claude-workspace/1673e4f1-5687-4e62-9ac9-ba60e37cfe8e/scratchpad/mock/photo_from_chat_8.jpg")

@unittest.skipUnless(PHOTO.exists(), "22 Nov photo not on this Mac")
def test_photo_reproduces_reference(self):
    ...  # segment PHOTO into a temp dir, brightness(box=(300, 120, 1150, 970), cols=66, rows=42);
         # assert every cell within 0.01 of the reference grid
```

Write the elided body from its comment. The photo lives in a scratch folder that can be wiped; a skip is expected then, and the reference grid stays the truth.

- [ ] **Step 2: Run them to see them fail.** Expected: FAIL (no `data/portrait.json`, no `brightness`).

- [ ] **Step 3: Implement `portrait.py`.** `brightness` follows `mockup.py`'s `brightness()` exactly: clamp `(m - 0.45) / 0.25`, autocontrast with cutoff `(2, 1)` inside mask > 140, `UnsharpMask(8, 220, 1)`, BOX resample, gamma 1.7, times the clamped mask, rounded to 2 decimals. `main()` takes `PHOTO [--box x0,y0,x1,y1]`, runs `swift tools/segment.swift` into a temp dir (never the repo), writes `data/portrait.json`. Create `data/portrait.json` now by copying the reference grid (with `rows`, `cols`, `grid` keys). Delete `data/portrait.txt`.

- [ ] **Step 4: Run the tests.** Expected: PASS (the photo test may skip; say so in the report).

- [ ] **Step 5: Commit.** `git add tools/portrait.py tools/segment.swift data/portrait.json tests/test_portrait.py && git rm -q data/portrait.txt && git commit -m "The portrait as a brightness grid, cut out with Apple Vision"`

---

### Task 3: Motion rules

**Files:**
- Create: `tools/motion.py`
- Test: `tests/test_motion.py`

**Interfaces:**
- Consumes: the grid from Task 2.
- Produces:
  - `RAMP = " .,:;i1tfLCG08@"`, `N_FRAMES = 8`, `FLIP_S = 1.6`, `CYCLE_S = 18`
  - `frames(grid: list[list[float]], seed: int = 11) -> list[list[str]]`: 8 frames, each a list of 42 strings of 66 signs; stdlib `random.Random(seed)` only.
  - `flip_css(prefix: str) -> str`: keyframes and classes `{prefix}f0`…`{prefix}f7`.
  - `type_css(prefix: str, j: int, edges: list[float], width: float) -> str`: keyframes and class `{prefix}v{j}` for line j's mask rect.
  - `still_css(prefix: str) -> str`: the `prefers-reduced-motion: reduce` block.
  - `visible_frames(css: str, progress: float) -> list[int]` and `mask_scale(css: str, j: int, progress: float) -> float`: tiny step-end evaluators over the generated CSS, used by tests and by Task 5.

- [ ] **Step 1: Write the failing tests:**

```python
def test_exactly_one_frame_at_every_moment(self):
    css = motion.flip_css("c")
    for i in range(8000):
        self.assertEqual(len(motion.visible_frames(css, i / 8000)), 1)

def test_typing_steps_land_on_letter_edges(self):
    adv = typeset.advances("Engineering with an editor's eye.", "voice", 19)
    edges, width = [0] + [a + 1.5 for a in adv], adv[-1] + 2
    css = motion.type_css("c", 0, edges, width)
    seen = {round(motion.mask_scale(css, 0, p / 10000) * width, 2) for p in range(0, 1201)}
    self.assertEqual(seen, {round(e, 2) for e in edges})
    self.assertAlmostEqual(motion.mask_scale(css, 0, 0.20) * width, edges[-1], places=2)
    self.assertEqual(motion.mask_scale(css, 0, 0.50), 0.0)

def test_one_motto_at_a_time(self):
    # line j's progress at loop time t is ((t + 18 - 6j) % 18) / 18
    ...  # for t in 0..18 s in 10 ms steps, count lines with mask_scale > 0; assert <= 1

def test_frames_deterministic_and_glitch_only_on_3_and_6(self):
    grid = json.load(open("data/portrait.json"))["grid"]
    a, b = motion.frames(grid), motion.frames(grid)
    self.assertEqual(a, b)
    self.assertEqual(len(a), 8); self.assertEqual(len(a[0]), 42); self.assertEqual(len(a[0][0]), 66)
    ...  # background cells (grid == 0) are " " in frames 0,1,2,4,5,7

def test_still_css_shows_frame_0_and_line_0(self):
    css = motion.still_css("c")
    self.assertIn("prefers-reduced-motion: reduce", css)
    self.assertIn(".cf0", css); self.assertIn(".cv0", css)
```

Write the two elided bodies yourself from their comments.

- [ ] **Step 2: Run them to see them fail.** Expected: FAIL (no module `motion`).

- [ ] **Step 3: Implement `tools/motion.py`.** Percentages formatted `f"{x:.4f}%"` so a frame's off and the next frame's on are the identical literal. Frame 0's keyframes start at opacity 1; frame 7 ends at opacity 1. Type keyframes: `(12·i/n, edges[i]/width)` for i in 0..n, then `(28 + 4·(n−i)/n, edges[i]/width)` for i from n down to 0, then `100%` scale 0, all `step-end`, delay `-18 + 6j` s. `still_css` sets every frame and mask `animation:none`, frame 0 opacity 1, others 0, line 0's mask `scaleX(1)`, lines 1 and 2 `scaleX(0)`. The evaluators parse only what these functions emit (step-end: the value of the last keyframe at or before `progress`).

- [ ] **Step 4: Run the tests.** Expected: all PASS.

- [ ] **Step 5: Commit.** `git add tools/motion.py tests/test_motion.py && git commit -m "Motion rules: one frame at a time, letters typed whole"`

---

### Task 4: The card

**Files:**
- Rewrite: `tools/neofetch.py` (`readout`, `build`, `main`; keep `uptime`, `Mono`)
- Modify: `README.md`
- Create: `assets/card.svg`, `assets/card-narrow.svg`
- Delete: `assets/card-light.svg`, `assets/card-dark.svg`, `assets/card-light-narrow.svg`, `assets/card-dark-narrow.svg`
- Test: `tests/test_card.py`

**Interfaces:**
- Consumes: `typeset.advances`, face `"voice"` (Task 1); `data/portrait.json` (Task 2); everything in `motion` (Task 3).
- Produces: `readout(stats: dict, today: date) -> list[tuple]`; `build(stacked: bool, today: date | None = None) -> str`; `main()` writes `assets/card.svg` and `assets/card-narrow.svg`. Class prefixes: `c` for the wide card, `n` for the narrow one.

- [ ] **Step 1: Write the failing tests:**

```python
STATS = {"created": "2017-09-26", "repos": 17, "contributed": 1, "stars": 2, "followers": 28,
         "commits": 441, "added": 57126, "deleted": 14744}

def test_readout_copy(self):
    rows = neofetch.readout(STATS, date(2026, 11, 22))
    self.assertEqual(rows, [
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
    for row in neofetch.readout(big, date(2027, 9, 25)) + [("pair", "Uptime", "10 years, 11 months, 30 days")]:
        if row[0] == "pair":
            self.assertLessEqual(len(row[1]) + 1 + (12 - len(row[1])) + 1 + len(row[2]), 52)

def test_card_rules(self):
    for stacked in (False, True):
        svg = neofetch.build(stacked, today=date(2026, 11, 22))
        self.assertNotIn("<text", svg); self.assertNotIn("@font-face", svg)
        self.assertLess(len(svg.encode()), 1_000_000)
        for k in range(8):
            self.assertIn(f'class="{"n" if stacked else "c"}f{k}"', svg)
        self.assertIn("prefers-reduced-motion", svg)
        self.assertIn("#0B3B2E", svg)
        for banned in ("WIN", "Creating Images", "spy", "FR"):
            self.assertNotIn(banned, svg)

def test_same_day_same_bytes(self):
    self.assertEqual(neofetch.build(False, today=date(2026, 11, 22)), neofetch.build(False, today=date(2026, 11, 22)))

def test_nightly_path_needs_no_numpy_or_pillow(self):
    # The Action installs only fonttools and uharfbuzz.
    code = ("import sys; sys.modules['numpy'] = None; sys.modules['PIL'] = None; "
            "sys.path.insert(0, 'tools'); import neofetch, stats")
    self.assertEqual(subprocess.run([sys.executable, "-c", code]).returncode, 0)
```

- [ ] **Step 2: Run them to see them fail.** Expected: FAIL (old readout; `build` takes a theme).

- [ ] **Step 3: Implement.** Pairs are `key + " " + "." * (12 - len(key)) + " " + value`, keys mid, dots mid at 60% opacity, values pale; title and section names pale, rules mid; readout width 52 columns at 12 px JetBrains Mono; the Commits value is `f"{commits:,} · Repos {repos} · Followers {followers}"`. Wide card 830 × 420 at the metrics in the spec's reference folder `mockup.py` (signs 8.6 px on 9.2 px rows from x 20, y 22; readout x 384 from y 40, 22 px leading; motto baseline y 372, 19 px). Narrow card: portrait centred on top, readout under it, motto last; drop the motto size until the longest motto fits with `typeset.fit`, and compute advances at that size. Mottos are outlined with `typeset.text(..., "voice", ...)` under a `<mask>` rect per line. Mottos, in order: "Engineering with an editor's eye.", "I speak Python, fashion and three human languages.", "Where the model meets the moodboard." `aria-label` and README alt: "Nihan Bayrak as a moving terminal readout: her portrait drawn in signs beside her details. Berlin." README becomes:

```html
<picture>
  <source media="(max-width: 600px)" srcset="assets/card-narrow.svg">
  <img src="assets/card.svg" width="100%" alt="Nihan Bayrak as a moving terminal readout: her portrait drawn in signs beside her details. Berlin.">
</picture>
```

- [ ] **Step 4: Run all tests.** Expected: all PASS.

- [ ] **Step 5: Generate the cards.** Run: `../github-profile/.venv/bin/python tools/neofetch.py`. Expected: prints `card.svg` and `card-narrow.svg`, each under 977 KB.

- [ ] **Step 6: Commit.** `git add tools/neofetch.py README.md assets/card.svg assets/card-narrow.svg tests/test_card.py && git rm -q assets/card-light.svg assets/card-dark.svg assets/card-light-narrow.svg assets/card-dark-narrow.svg && git commit -m "The living card: one green, moving, personal"`

---

### Task 5: Playback check in a real browser

**Files:**
- Create: `tools/check_live.py` (adapted from the spec folder's `live_check.py`)

**Interfaces:**
- Consumes: `assets/card.svg`, `assets/card-narrow.svg`.
- Produces: `/opt/anaconda3/bin/python tools/check_live.py [--webkit]`, exit 0 when every check passes.

- [ ] **Step 1: Write the check.** Two pages per card. **Inline** (the SVG pasted into the page, so the DOM is readable): over 8 s of `requestAnimationFrame`, exactly one `.{p}f*` group at opacity 1 every sample, and at most one `.{p}v*` mask with scale above 0. **As `<img>`** (how GitHub shows it): a screenshot of the portrait area every ~250 ms, none below 30% of the median ink. Print the counts; exit 1 on any failure.

- [ ] **Step 2: Run it.** Run: `/opt/anaconda3/bin/python tools/check_live.py`. Expected: one frame visible in 100% of samples, never two mottos, 0 blank screenshots, for both cards. Then `--webkit`; if Playwright has no WebKit, say so in the report and do not install it.

- [ ] **Step 3: Compare the face.** Open `docs/superpowers/specs/2026-11-22-living-card/approved-mockup.html` and `assets/card.svg` side by side in a browser and screenshot both. The face must read the same. Put the screenshot in the report.

- [ ] **Step 4: Commit.** `git add tools/check_live.py && git commit -m "Check the card plays cleanly in Chrome"`

---

### Task 6: The repo holds only the card

**Files:**
- Delete: `assets/object.webp`, `assets/octopus.webp`, `assets/title-dark.svg`, `assets/title-light.svg`, `data/materials.json`, `data/nautilia-octopus.obj`, `tools/render.py`, `tools/swim.py`, `tools/shade.py`, `tools/model3d.py`, `tools/export-object.py`, `tools/title.py`, `tools/variants.py`, `tools/fonts/CormorantInfant.ttf`, `tools/fonts/ArchivoNarrow.ttf`
- Modify: `tools/typeset.py` (drop faces `display`, `display_med`, `fact`, `fact_bold`)
- Test: `tests/test_repo.py`

**Interfaces:**
- Consumes: everything from Tasks 1–5. Keeps `data/profile.toml`, `data/work.json`, `tools/export-site-data.py` (her portfolio site reads them).

- [ ] **Step 1: Write the failing test:**

```python
GONE = ["assets/object.webp", "assets/octopus.webp", "assets/title-dark.svg", "assets/title-light.svg",
        "data/materials.json", "data/nautilia-octopus.obj", "tools/render.py", "tools/swim.py",
        "tools/shade.py", "tools/model3d.py", "tools/export-object.py", "tools/title.py",
        "tools/variants.py", "tools/fonts/CormorantInfant.ttf", "tools/fonts/ArchivoNarrow.ttf"]
KEPT = ["data/profile.toml", "data/work.json", "tools/export-site-data.py"]

def test_only_the_card_remains(self):
    tracked = set(subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split())
    self.assertFalse(tracked & set(GONE))
    self.assertTrue(set(KEPT) <= tracked)
    self.assertEqual(set(typeset.FACES), {"mono", "mono_bold", "mono_light", "voice"})
```

- [ ] **Step 2: Run it to see it fail.** Expected: FAIL (files still tracked).

- [ ] **Step 3: Remove them.** `git rm -q` each path in `GONE`; delete the four faces from `FACES`.

- [ ] **Step 4: Run the whole suite and both tools.** Run: `../github-profile/.venv/bin/python -m unittest discover -s tests -v`, then `../github-profile/.venv/bin/python tools/neofetch.py` and `../github-profile/.venv/bin/python tools/export-site-data.py`. Expected: all PASS; both tools run; `git status` shows no change to `assets/card*.svg` or `data/work.json`.

- [ ] **Step 5: Commit.** `git add tools/typeset.py tests/test_repo.py && git commit -m "The repo holds only the card"`

---

### Task 7: Notes, rebase, preview

**Files:**
- Modify: `CLAUDE.md` (sections "What this is", "Design", "Editing", "Dependencies")

- [ ] **Step 1: Update `CLAUDE.md`.** The card is now the living card from the spec: one green card plus a narrow cut, `data/portrait.json` from `tools/portrait.py` (Apple Vision, Mac only), motion rules in `tools/motion.py`, Fraunces italic in `tools/fonts/`, tests via `unittest`, playback via `tools/check_live.py`. Replace "Direction B, editorial" with the green palette and point to the spec. Delete the sections "The renderer" and "The object" and the octopus paragraph, since their code is gone (say once that history keeps them, last full page `fff297d`). Keep "One source for the project list".

- [ ] **Step 2: Rebase.** Run: `git fetch origin && git rebase origin/main`. A conflict on a themed card is the nightly bot redrawing a file this branch deletes: resolve with `git rm` on that card. Rerun the tests and `tools/neofetch.py`; commit any change to the cards.

- [ ] **Step 3: Commit.** `git add CLAUDE.md && git commit -m "Notes for the living card"`

- [ ] **Step 4: Push the preview (approved by Nihan, 22 Nov: preview branch only).** Run: `git push -u origin living-card`. Expected: a new remote branch. Never push `main`.

- [ ] **Step 5: Hand over.** Give Nihan the link `https://github.com/nihanbayrak/nihanbayrak/tree/living-card` to view the README on github.com, light and dark, wide and narrow. Merging to `main`, making the repo public, and the sidebar changes are hers.
