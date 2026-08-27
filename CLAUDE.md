# github-profile

The `nihanbayrak/nihanbayrak` profile README — the page GitHub shows above her repositories.

## What this is

Every visual is generated, not hand-drawn. `tools/render.py` pulls live numbers from
the GitHub API and typesets SVGs into `assets/`. A nightly Action re-runs it and commits
the diff.

## The one hard constraint

GitHub renders README images inside `<img>`, which blocks external font loading. **All
type must be converted to outlines.** `tools/typeset.py` does this with HarfBuzz (shaping,
so kerning survives) and fontTools (outlines). Never add a `<text>` element or an
`@font-face` — it will render in Times on someone else's machine.

Layout measures itself: use `T.wrap()` and `T.fit()` rather than guessing at widths.

## Design

Governed by `ninu-design` in the executive-assistant repo. Era tag: `19c-engraved-broadside`
— ruled information cells, a table pretending to be a poster. Palette is the Wibar draw,
three values only: cornflower ground `#8FA8DC`, oxblood ink `#8B2027`, cream structure
`#F2EBD8`. Grain and halftone on every surface; nothing ships flat.

## Editing

Copy and the project list live in `data/profile.toml`. Change that, not the renderer.

```bash
pip install fonttools uharfbuzz brotli
GITHUB_TOKEN=$(gh auth token) python tools/render.py
```

**Verify in a browser before pushing.** These bugs are invisible in the source — the first
draft had a broken keyhole, colliding table cells and three overflowing text runs, none of
which were visible by reading the SVG.

## The Action races you

`refresh.yml` runs on any push touching `tools/**` or `data/**` and commits its own
redraw. Always `git pull --rebase` before rendering locally, or your next push is
rejected. Its numbers are usually fresher than yours — but note it runs with a
repo-scoped `GITHUB_TOKEN` that cannot see private repositories, so anything derived
from private repos will differ between a local run and a CI run. That is exactly why
the stack is stated in `profile.toml` rather than counted.

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
