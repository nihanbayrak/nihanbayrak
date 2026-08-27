# github-profile

The `nihanbayrak/nihanbayrak` profile README — the page GitHub shows above her repositories.

## What this is

One generated image and words. `tools/render.py` writes a single asset, `assets/object.svg`
— the turning octopus. Everything else on the page is markdown.

Until 27 Aug there were also a banner, a live ledger and six work cards, all drawn from the
GitHub API and redrawn nightly. Nihan cut them: one object, and the words do the rest. They
are in the history if they are ever wanted back, and the three rejected banner directions
are still in `tools/variants.py`. Nothing reads the API now, so the render is deterministic
and the nightly schedule is gone with it.

## The one hard constraint

GitHub renders README images inside `<img>`, which blocks external font loading. **All
type must be converted to outlines.** `tools/typeset.py` does this with HarfBuzz (shaping,
so kerning survives) and fontTools (outlines). Never add a `<text>` element or an
`@font-face` — it will render in Times on someone else's machine.

Layout measures itself: use `T.wrap()` and `T.fit()` rather than guessing at widths.

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

`assets/object.svg` is a real 3D mesh turning: `data/nautilia-octopus.obj`, 12,137
triangles, clustered down from the 90k original by `tools/model3d.py`.

`tools/engrave.py` renders it. Each frame is rasterised with a z-buffer and one lamp,
and the resulting **tone** is then cut as hatching — parallel lines at a fixed screen
angle whose stroke *weight* carries the shading. Do not be tempted to emit the mesh as
polygons instead: forty frames of flat-shaded triangles is megabytes of path data and
looks like a screensaver. Output size scales with hatch lines, not with the mesh.

Three things that are easy to get wrong here, all of which were:

- **Normals must be computed in camera space, not from projected pixels.** Screen x and
  y are multiplied by the scale and z is not, so a cross product taken over there has a
  meaningless z and lights the whole model flat.
- **Winding is not consistent** across the model's 427 parts. Whatever the z-buffer
  keeps is by definition facing the viewer, so flip every normal toward the camera and
  light one-sided from there.
- **A one-pixel crease prints as nothing.** Hatch lines are ~12px apart; depth
  discontinuities have to be widened before the engraver's lines can cross them.

The hatching is fixed to the plate, not to the object — it must not turn with it.
There is deliberately no paper fill under the animal, so the card's grain reads through.

## Dependencies

`fonttools uharfbuzz brotli numpy`. `render.py` imports all of them at module level, so
a missing one breaks the whole render, not just the piece that needs it. Keep the
workflow's pip line and this list in step.
