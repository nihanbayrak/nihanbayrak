# github-profile

The `nihanbayrak/nihanbayrak` profile README — the page GitHub shows above her repositories.
This is her **personal** account; company work lives on separate accounts, so the card names
no employer.

## What this is

One card: **the living card**, her call on 22 Nov. A neofetch readout of her, after the
terminal-card style of Andrew Grant's profile, that moves: her portrait in signs re-inked as
an eight-frame flipbook, key and value pairs joined by leader dots, GitHub numbers at the
foot, and three mottos typing themselves out in turn. Design and the reasons behind every
choice: `docs/superpowers/specs/2026-11-22-living-card-design.md`. The approved mockup and
the approved face sit beside it in `docs/superpowers/specs/2026-11-22-living-card/`.

- `tools/portrait.py PHOTO` writes `data/portrait.json`: a 42 × 66 brightness grid. Mac
  only: she is cut out with Apple Vision (`tools/segment.swift`). **Her photo never enters
  the repo**, nor its mask; both stay in a temporary folder. The approved face is
  `portrait-reference.json` in the spec folder; `data/portrait.json` equals it.
- `tools/stats.py` writes `data/stats.json`: public non-fork repos, stars, followers,
  commits since the account opened, and lines of code from her own commits. The gh CLI by
  hand, the workflow's `GITHUB_TOKEN` in Actions; no token in the repo.
- `tools/motion.py` holds every animation rule as plain functions (frames, flip CSS, typing
  CSS, reduced motion) and can read its own CSS back, so the rules are unit-tested.
- `tools/neofetch.py` writes `assets/card.svg` (830 × 420) and `assets/card-narrow.svg`
  (stacked, for phones). The readout's words live in `readout()` and the mottos in
  `MOTTOS`; they are hers, word for word. Change them there and in the README's alt text.
- `refresh.yml` reruns stats and the card daily at 04:17 UTC and commits if they moved.

Older pages (the swimming octopus, the "Harness engineer" title, the editorial and broadside
directions) are in the history only; the last full page of that era is `fff297d`.

## Motion: two rules that were wrong first

- **Frames share one cycle.** Every portrait frame runs the same step-end animation with no
  delay; frame k's window is in its own keyframes, so one frame's "off" and the next one's
  "on" are the same value. Eight animations staggered by delay left gaps where the face
  blinked out.
- **Letters are measured.** The motto masks step to each letter's right edge from HarfBuzz
  (`typeset.advances`). A guessed average width showed half letters and stalled at the end.

## Type in an image

GitHub renders README images inside `<img>`, which blocks external font loading, so any
type in an SVG must be converted to outlines. `tools/typeset.py` does that with HarfBuzz
and fontTools: JetBrains Mono for the portrait and readout, Fraunces italic (OFL, from
google/fonts) for the mottos. The moment a `<text>` element or an `@font-face` goes into an
asset, it renders in Times on someone else's machine. A test checks for both.

## Design

Governed by `ninu-design` in the executive-assistant repo, and by her calls in the spec.
One deep green in three depths, painted by the card so it is the same on GitHub's light and
dark themes: ground `#0B3B2E`, mid `#4FA383`, pale `#D3F2E4`. Grain on every surface;
nothing ships flat.

## Editing and checking

```bash
python -m venv .venv && .venv/bin/pip install numpy pillow fonttools uharfbuzz
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/neofetch.py
/opt/anaconda3/bin/python tools/check_live.py      # Playwright + the Mac's Chrome
```

No token needed. The shell has conda base active, so use a venv or the installs land in
`/opt/anaconda3`. `check_live.py` plays both cards in headless Chrome, inline and as an
`<img>`, and fails if more than one portrait frame or motto shows at once or the face goes
blank. **Look at the cards in a browser before pushing**: layout bugs are invisible in the
SVG source.

## Two things will overwrite you

`refresh.yml` runs daily and on a push to `main` touching `tools/**` or `data/**`: it
refetches the stats, redraws the card, and commits if anything moved (Uptime alone moves
it every day). The render is deterministic (a test checks two runs on the same day give the
same bytes), but `git pull --rebase` before pushing anyway.

**A second session works in this repo.** On 26 Aug it swept an untracked `tools/sort3d.py`
into a commit with `git add -A` during a rebase and broke the nightly redraw. Check
`git log` and `git status` before assuming local state is yours, and stage specific paths
during a conflict, never `-A`.

## One source for the project list

`data/profile.toml` is authoritative. `tools/export-site-data.py` regenerates
`data/work.json`, which is copied into the portfolio site's `data/`. Edit the toml,
run the script, copy the file — never hand-edit `work.json` in either repo. Not part of the
card, but kept: the portfolio site reads it.

## Dependencies

The nightly job needs only `fonttools` and `uharfbuzz`; the workflow pins them (fonttools
4.63.0, uharfbuzz 0.56.0) because it runs unattended, and a test fails if the card's path
starts needing numpy or Pillow. `tools/portrait.py` (numpy, Pillow, Swift) and
`tools/check_live.py` (Playwright) run only on her Mac. Keep the workflow's pip line and
this list in step.
