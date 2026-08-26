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
