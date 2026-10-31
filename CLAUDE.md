# github-profile

The `nihanbayrak/nihanbayrak` profile README — the page GitHub shows above her repositories.

## What this is

Two images and nothing else, by Nihan's call on 1 Nov: the octopus swimming, and the
words **Harness engineer** under it. No background, no other text.

- `tools/render.py` writes `assets/octopus.webp`: 40 frames, 4 s a loop, transparent,
  the shadow in the alpha so it swims on either GitHub theme. `tools/swim.py` bends the
  mesh each frame: the dome stays rigid, a travelling wave runs down each arm out of step
  with its neighbours, the arms open and close in two strokes a loop, the body rides each
  stroke, and the animal turns a little either way.
- `tools/title.py` writes `assets/title-{light,dark}.svg`: the two words in Cormorant
  Infant Light as outlines, tobacco ink on light and paper ink on dark, picked through
  `<picture>`.

Everything the page carried before (the 1922 sheet, the clockwork headline, Yao's
kaleidoscope on Klein blue, the year the small octopus ate, the three cards and their case
files, the one-image composer) is in the history: the last commit with all of it is
`fff297d`. `assets/object.webp`, the old turntable, predates this round and is unused;
Nihan has not said whether to delete it.

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

## Type in an image

GitHub renders README images inside `<img>`, which blocks external font loading, so any
type in an SVG must be converted to outlines. `tools/typeset.py` does that with HarfBuzz
and fontTools, and `title.py` uses it. The moment a `<text>` element or an `@font-face`
goes into an asset, it renders in Times on someone else's machine.

## Design

Governed by `ninu-design` in the executive-assistant repo. **Direction B — editorial**,
chosen by Nihan on 26 Aug after she rejected the broadside direction outright: warm paper
`#F5F1E8`, near-black `#1A1611`, one oxblood mark `#8B2027`, two typefaces. This file used
to name a cornflower broadside palette that was never shipped. Grain on every surface;
nothing ships flat.

One accent per piece, and on the object it is spent on the two eye lenses — the surface a
press would actually ink.

## Editing

The README is two pictures. The words live in `tools/title.py`; change them there and in
the README's alt text. `data/profile.toml` no longer feeds the README; it survives as the
source for the portfolio site (see below).

```bash
python -m venv .venv && .venv/bin/pip install numpy pillow fonttools uharfbuzz
.venv/bin/python tools/render.py && .venv/bin/python tools/title.py
```

No token needed any more. The shell has conda base active, so use a venv or the installs
land in `/opt/anaconda3`.

**Verify in a browser before pushing.** These bugs are invisible in the source — the first
draft had a broken keyhole, colliding table cells and three overflowing text runs, none of
which were visible by reading the SVG.

## Two things will overwrite you

`refresh.yml` runs on a push to `main` touching `tools/**` or `data/**`, re-renders the
octopus and the title, and commits if anything moved. There is no nightly run any more.
The render is deterministic, so it should not produce a diff, but `git pull --rebase`
before pushing anyway.

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
rides in the alpha channel rather than on a painted floor. The canvas is 900 × 460 (rendered
at 1.25×), the animal centred and its shadow falling left into the room that leaves.
`shade.py` blurs the shadow with `np.roll`, which **wraps**: anything that reaches one edge
reappears on the other, so keep a margin round the shadow if you reframe.

## Dependencies

`numpy pillow` for `render.py`; `fonttools uharfbuzz` for `title.py`. The workflow pins
all four (numpy 2.5.2, pillow 12.3.0, fonttools 4.63.0, uharfbuzz 0.56.0) because it runs
unattended. Keep its pip line and this list in step.
