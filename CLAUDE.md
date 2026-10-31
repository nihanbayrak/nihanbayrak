# github-profile

The `nihanbayrak/nihanbayrak` profile README — the page GitHub shows above her repositories.

## What this is

Two printed pieces and some markdown, laid out under `ninu-design`
(`NB_executive_assistant/.claude/skills/ninu-design`), applied on 24 Oct:

- **Era:** `victorian-automaton-3d`, from the brass-and-enamel octopus automaton in her
  moodboard (`Screenshot 2026-08-27 at 11.25.54`), one built object on a cream ground with
  one soft shadow. The page under it borrows the 1922 Ladies' Home Journal page.
- **The octopus.** `tools/render.py` writes `assets/object.webp`: the octopus turning, on a
  transparent ground with the shadow in the alpha. It sat on grained paper for one round;
  Nihan asked for it transparent again on 24 Oct, so it floats on GitHub's own page above
  the paper sheet. `shade.turntable(background=True)` still paints the paper if wanted.
- **The sheet.** `tools/dance.py` writes `assets/intro{,-narrow}.svg`: a ruled panel of
  small-caps facts, a gold hairline between columns, the headline, a deck, and body with a
  drop cap. Cormorant Infant Light is the character, Libre Baskerville does the reading,
  Archivo Narrow carries the facts. The copy is four sentences (1 Nov), written in the
  register of Andrew Ng and Dario Amodei at her request: judgment is the bottleneck now.
- **Klein, by her call on 1 Nov.** Every piece is printed on International Klein Blue
  `#002FA7` with white type and one gold accent `#D9B44A` (Klein's third colour, and the
  octopus's brass). With its own ground, each piece needs no light or dark version: one
  file per width, `<picture>` picks the narrow cut at 600 px and under. Before this the
  pieces were transparent with theme inks (25 Oct), and before that printed on paper.
- **The kaleidoscope** behind the intro is Yao's (`~/claude_workspace/yao/src/ui/Kaleidoscope.tsx`)
  ported to SVG: 56 bars and square-holed coins in one 30 degree wedge, clipped and mirrored
  twelve times with `<use>`, the tube turning in 140 s and the pieces drifting in 16 s.
  Tones of the ground's own blue plus faint gold and white, so the words lead.
- **The cards.** `tools/cards.py` writes `assets/card-{1,2,3}{,-narrow}.svg`, one
  label per job, each its own link: the object you choose (her §1d references), since a
  click is the one thing a README allows. A manicule ☞ (Cormorant carries it) beside the
  printed verb steps forward in the same clockwork as the headline. The proof sits under
  each card in a `<details>` case file, the other thing a README allows: opening something.
  Principles and colophon fold away the same way. Run it from `tools/` after `dance.py`.

- **The year, eaten.** `tools/commits.py` fetches the contribution calendar (the
  workflow's `GITHUB_TOKEN` at night, the `gh` CLI by hand, so no token touches this
  repo), keeps it in `data/contributions.json`, and writes `assets/commits{,-narrow}.svg`:
  a halftone dot per day sized by GitHub's quartile, and a small octopus that walks the year
  one week per held step, eating each column; eaten dots grow back in order. The narrow cut
  shows the last 26 weeks. `--draw` redraws from the saved JSON without fetching.
- **The nightly run is back** (`refresh.yml`, 04:17 UTC) for the graph only; the octopus
  render runs on pushes. It commits to `main` every night, so a long lived branch that
  touches `assets/commits-*` or `data/contributions.json` will conflict: take main's copy.

Nihan first asked for hover, then for the whole text to dance. A README cannot hover (no
script, and pointer events never reach an image), and her own skill keeps body text still,
so the display line carries the motion. The copy lives in `dance.py` and again in the
README's alt text: change both together. `dance.py` needs fonttools and uharfbuzz, which
the workflow does not install, so the Action never calls it: run it by hand and commit both
SVGs. Everything from the links line down is markdown.

**No dashes in the copy.** Nihan's rule from 24 Oct: no em or en dashes in the README, and
avoid hyphenated words where a plain phrase works.

Two rounds of cutting got it here. Until 27 Aug there were also a banner, a live ledger and
six work cards drawn from the GitHub API and redrawn nightly; Nihan cut them. The object
itself was then an engraving — the mesh rasterised and re-cut as hatch lines, so the whole
thing stayed vector — and she cut that too: **it has to look like the model.** A shaded
surface is a continuous gradient, so the page is raster now.

Everything is in the history. The engraved renderer is `tools/engrave.py` at commit
`9300246`, and the three rejected banner directions are still in `tools/variants.py`.

## One image, no gaps (1 Nov)

Nihan asked for everything on one background with no gaps, and for the octopuses to
really move. GitHub puts space between any two README images, so the visual page is now
**one SVG**: `tools/page.py` writes `assets/page.svg` and `assets/page-narrow.svg` (600 px
and under, through `<picture>`). It nests every piece on one Klein blue ground: the
octopus, the intro sheet (`dance.build`), the year (`commits.build`), a "Pick a card"
header, and the three cards (`cards.build`), renaming each piece's glyph ids so they stay
unique. The cards are no longer separate links (one image is one click); the case files
under the image carry the links.

- **The octopus swims.** `tools/swim.py` bends the mesh every frame: the dome stays
  rigid, the arms carry a travelling wave out of step with each other, open and close in
  two strokes a loop, the body rides each stroke, and the animal turns a little either
  way. `tools/render.py` writes 40 frames to `assets/octopus/f00..f39.webp` on Klein blue
  (shade.py now takes `sh.ground`), and `page.py` carries them inside the SVG as data
  URIs, shown one at a time. About 1.3 MB per page file. `assets/object.webp` is the old
  turntable and nothing uses it any more.
- **The small octopus glides** through the year at an even pace, bobbing, its arms
  morphing between two sways with SMIL `<animate>`; no more clockwork steps there.
- **The kaleidoscope fades** in and out at the top and bottom of the intro through
  ground-coloured gradient veils, so it has no edge where the octopus meets it.
- **Order of work:** `render.py` (only when the swim changes), `commits.py` (fetches the
  calendar), `page.py` (draws everything). The workflow runs the same three; at night it
  skips the render. The page is redrawn nightly, so expect a ~1.3 MB file change per night.

## The renderer

`tools/shade.py`. Three things in it were wrong first and are worth not repeating:

- **Cull back faces by the vertex normals, not by the winding.** This model's winding is
  consistent but *inverted* relative to its normals, and roughly 8% of triangles disagree
  with it outright — culling on the projected area sign punches holes in the animal.
- **Cluster vertices inside each part, never across parts.** The model is 427 objects that
  touch but share no geometry. Weld them and the brass bands smear into the arms, in the
  decimation and again in the smooth normals.
- **Shade deferred.** The triangle loop writes only depth, normal and material id; the
  lighting runs once per frame over the whole buffer. Per-triangle shading costs about
  three times as long for the same picture.

Material values are not invented. They are the PBR figures out of the source GLB, kept in
`data/materials.json`, in **linear light** — convert to sRGB on the way out, not before.

The lamp is fixed to the camera, not to the world, so the highlight holds still while the
animal turns. A world-fixed lamp makes it sweep and strobe.

## If type ever returns to an image

GitHub renders README images inside `<img>`, which blocks external font loading, so any
type in an SVG must be converted to outlines — `tools/typeset.py` does that with HarfBuzz
and fontTools. Nothing calls it today; the page's words are all markdown. Keep it: the
moment a `<text>` element or an `@font-face` goes into an asset, it renders in Times on
someone else's machine.

## Design

Governed by `ninu-design` in the executive-assistant repo. **Direction B — editorial**,
chosen by Nihan on 26 Aug after she rejected the broadside direction outright: warm paper
`#F5F1E8`, near-black `#1A1611`, one oxblood mark `#8B2027`, two typefaces. This file used
to name a cornflower broadside palette that was never shipped. Grain on every surface;
nothing ships flat.

One accent per piece, and on the object it is spent on the two eye lenses — the surface a
press would actually ink.

## Editing

The page's copy is now markdown in `README.md` — edit it there. `data/profile.toml` no
longer feeds the README; it survives as the source for the portfolio site (see below), so
**the project list exists in two places and can drift.** Change one, check the other.

```bash
python -m venv .venv && .venv/bin/pip install fonttools uharfbuzz brotli numpy
.venv/bin/python tools/render.py
```

No token needed any more. The shell has conda base active, so use a venv or the installs
land in `/opt/anaconda3`.

**Verify in a browser before pushing.** These bugs are invisible in the source — the first
draft had a broken keyhole, colliding table cells and three overflowing text runs, none of
which were visible by reading the SVG.

## Two things will overwrite you

`refresh.yml` runs on a push to `main` touching `tools/**` or `data/**` and commits its own
redraw. It is much less dangerous than it was — the render is deterministic now, so it
should never produce a diff — but `git pull --rebase` before pushing anyway.

**A second session works in this repo.** On 26 Aug it swept an untracked `tools/sort3d.py`
into a commit with `git add -A` during a rebase and broke the nightly redraw. Check
`git log` and `git status` before assuming local state is yours, and stage specific paths
during a conflict, never `-A`.

## One source for the project list

`data/profile.toml` is authoritative. `tools/export-site-data.py` regenerates
`data/work.json`, which is copied into the portfolio site's `data/`. Edit the toml,
run the script, copy the file — never hand-edit `work.json` in either repo.

## The object

`data/nautilia-octopus.obj` — 37,327 triangles, clustered down from the 90k original by
`tools/model3d.py`, materials and part boundaries intact. `tools/export-object.py` renders
the same object with no page around it, for use elsewhere.

The published image is transparent, so it sits on either GitHub theme, and the cast shadow
rides in the alpha channel rather than on a painted floor.

Since 24 Oct it is the page's centred hero, shown at 700 wide above the name, and the
canvas is 1234 × 706. The lamp sits upper right, so the shadow runs about 190 px left of
the animal; at the old 520-wide canvas it was cut off in 37 of 48 frames. The empty right
side matches the shadow's room on the left so the body stays centred under the name.
`shade.py` blurs the shadow with `np.roll`, which **wraps** — anything that reaches one
edge reappears on the other, so keep a margin round the shadow if you reframe.

## Dependencies

`numpy pillow` — that is all `render.py` needs. `fonttools uharfbuzz brotli` are only for
`typeset.py` and `variants.py`, which nothing in the render path calls; install them if you
touch those. Keep the workflow's pip line and this list in step.
