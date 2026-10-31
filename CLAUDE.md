# github-profile

The `nihanbayrak/nihanbayrak` profile README — the page GitHub shows above her repositories.

## What this is

One card, by Nihan's call on 1 Nov: a neofetch readout of her, after the terminal-card
style of Andrew Grant's profile, with her own content and this repo's own code. A portrait
in signs on the left, key and value pairs joined by leader dots on the right, GitHub
numbers at the foot.

- `tools/portrait.py PHOTO` writes `data/portrait.txt`: signs only (` .`',:;-~+=*%#&$@`),
  the wall dropped by colour, the face equalised inside that mask, edges darkened. **Her
  photo never enters the repo**; only the characters do. Default crop is her close-up,
  head and shoulders, 46 columns by 26 rows.
- `tools/stats.py` writes `data/stats.json`: public non-fork repos, stars, followers,
  commits since the account opened (plus GitHub's restricted count), and lines of code from
  her own commits on each public repo. A commit moving more than 50,000 lines is a data
  file, not code, and is skipped: one CSV added and deleted would swing it by 2.8 million.
  The gh CLI by hand, the workflow's `GITHUB_TOKEN` in Actions; no token in the repo.
- `tools/neofetch.py` writes `assets/card-{light,dark}{,-narrow}.svg`, all type outlined
  JetBrains Mono so it never falls back to Times. Uptime counts from the account's
  opening day. The readout's content lives in `readout()`; hobbies and the IDE line are
  inferred, not stated by her, so check them with her before trusting them.
- `refresh.yml` reruns stats and the card daily at 04:17 UTC and commits if they moved.

The swimming octopus and the "Harness engineer" title (`render.py`, `swim.py`, `title.py`,
`assets/octopus.webp`, `assets/title-*.svg`) are still in the repo but not on the page.
Everything older is in the history; the last full page is `fff297d`.

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

The README is one `<picture>`. The card's words live in `tools/neofetch.py`; change them
there and in the README's alt text. `data/profile.toml` no longer feeds the README; it survives as the
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

`refresh.yml` runs daily and on a push to `main` touching `tools/**` or `data/**`: it
refetches the stats, redraws the card, and commits if anything moved (Uptime alone moves
it every day).
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
