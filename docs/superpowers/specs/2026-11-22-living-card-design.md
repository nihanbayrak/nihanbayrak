# The living card: design

22 Nov 2026. Approved by Nihan in conversation, from moving mockups (direction "A1").
Replaces the still neofetch card that `main` draws today.

## Intent

`nihanbayrak` is Nihan's **personal** GitHub account; company work lives on separate
accounts. The profile should read as hers: an AI engineer with a designer's and an
editor's eye, multidisciplinary, and someone a team like Anthropic's would recognise as
thinking the way they do, without the page ever saying "hire me".

The card she already has (a portrait in signs beside a neofetch readout, after Andrew
Grant's profile) is the right form. What it lacks: it is still, it names her employer, and
its palette is GitHub's own. The living card keeps the form and adds three things:

1. **Motion.** The portrait shimmers like a flipbook and a line of italic types itself out,
   in turn, three mottos.
2. **Her colour.** One deep green in three depths, painted by the card itself, so it looks
   the same on GitHub's light and dark themes and sits well beside the green contribution
   graph.
3. **Personal copy.** No company. Every line is something she can point to.

## Goals

- The face reads as Nihan at a glance. The approved portrait comes from the photo she
  sent on 22 Nov (red hair, denim shirt, name tag), cut out on her Mac, cropped to face
  and hair. She said of this version: "my face was perfectly matched". Matching it is the
  first acceptance test.
- The card moves on github.com, inside the README `<img>`, with no JavaScript.
- Numbers stay true: the daily Action keeps refreshing them.

## Non-goals

- Restyling GitHub itself (impossible: no CSS or scripts on the profile page).
- The profile sidebar, pins and making the repo public. Those are clicks in her GitHub
  settings; see "Her side" at the end.
- An interactive or WebGL version, a GitHub Pages site, AI-generated imagery.
- The kaleidoscope and halftone directions that were shown and set aside.

## Anti-goals: it has failed if

- Any type renders in Times on someone else's machine (a `<text>` element or `@font-face`
  in the asset).
- The face ever blinks out between frames, or a typed letter appears cut in half. Both
  happened in early mockups and were fixed; see "Motion".
- Two mottos show at once.
- It names WIN Creating Images, says "not a spy", or reads like a job application.
- Her photo, or anything that can rebuild it beyond the sign grid, enters the repo.

## What it looks like

A single card, 830 × 420, on deep viridian. Left: the portrait in ASCII signs, 66 columns
by 42 rows. Right: the readout. Bottom right: the typed motto.

### Colour

| Role | Value | Used for |
|---|---|---|
| ground | `#0B3B2E` | the whole card |
| mid | `#4FA383` | keys, leader dots, rules |
| pale | `#D3F2E4` | portrait signs, values, title, motto |

Light grain over everything (`feTurbulence`, about 8% opacity, screen blend). Nothing
ships flat (her design system's rule). One card serves both GitHub themes; it paints its
own ground.

### Type

- **JetBrains Mono** for the portrait and the readout (already in `tools/fonts/`).
- **Fraunces italic, weight 300** for the motto, 19 px. **Not in the repo yet.** It is
  OFL-licensed (Google Fonts / `undercasetype/Fraunces`). Downloading it into
  `tools/fonts/` needs Nihan's go-ahead at build time: name the exact file and source.
- All of it outlined through `tools/typeset.py`, as today.

### The readout

```
nihan@bayrak ───────────────────────────────────────
Based ....... Berlin · TR, EN, DE
Uptime ...... 9 years, 1 month, 27 days          ← computed daily, as today
Kernel ...... Evals, agents, honest interfaces
Shell ....... Claude Code, zsh

─ Now ──────────────────────────────────────────────
Measuring ... Can an LLM judge copyright risk?
Designing ... Conscious Eyes: the label, at a glance
Guarding .... Prompt-injection scans for chat logs

─ GitHub ───────────────────────────────────────────
Commits ..... 438 · Repos 16 · Followers 29      ← live from data/stats.json
```

Words are hers as approved; do not reword them. Decisions behind them:
- Languages are TR, EN, DE only (she removed FR).
- "Designing" not "Shipping", and not "never invents an ingredient": she rejected that as
  Conscious Eyes' motto and wanted a product designer's line.
- "Measuring" points at the public repo `llm-copyright-judge-eval`.
- "Guarding" is the private `ai-security-analyzer`; it stays unless she says otherwise.

### The mottos

One at a time, in this order, on an 18-second loop (6 s each):

1. *Engineering with an editor's eye.*
2. *I speak Python, fashion and three human languages.*
3. *Where the model meets the moodboard.*

She rejected "Half engineer, half art director, fully in the loop", "not a spy, just an
engineer", and the safety-flavoured set ("I build things that would rather say 'I don't
know.'", "Evals first. Then the demo.", "Taste is a safety feature.").

## Motion

Two animations, CSS only, inside the SVG.

**Portrait flipbook.** 8 frames, 1.6 s per loop (200 ms a frame). Every frame is the same
brightness grid with fresh ±0.09 jitter, so the signs shimmer; frames 3 and 6 also slip a
band of 3 rows sideways by 2 or 3 columns, a signal glitch.

How frames switch matters; the first version got it wrong. Every frame runs **the same
animation duration, no delay, `step-end` timing**, and frame *k*'s visible window is
written into its own keyframes (`k/8` to `(k+1)/8`). One frame's "off" and the next one's
"on" are the same keyframe value, so exactly one frame is visible at every instant.
Timing eight separate animations with staggered delays left sub-millisecond gaps where no
frame showed and the face blinked.

**Typed motto.** Each line sits under a mask whose width steps, glyph by glyph, to that
glyph's right edge plus 1.5 px for italic overhang. Type over 12% of the loop, hold until
28%, erase back glyph by glyph by 32%, then stay hidden while the next line has its turn.
Edges come from **HarfBuzz advances for the exact face and size** (`typeset.shape`). The
first version guessed an average glyph width and revealed half letters with a dead pause
at the end.

**Reduced motion:** under `prefers-reduced-motion: reduce`, show frame 0 and motto 1 in
full, still. Complete at rest.

## Phones

A stacked cut for `max-width: 600px`, swapped in by the README's `<picture>` as today:
portrait on top, readout under it, motto last. Same colour, same motion. *(My call: the
mockups never showed a phone layout. Nihan sees it in review.)*

## How it is made

Keep the existing pipeline and its rules (`CLAUDE.md`); change these parts.

- **`tools/portrait.py`** is rewritten. Input: her photo, run by hand on a Mac. It cuts her
  out with Apple Vision person segmentation (`VNGeneratePersonSegmentationRequest`,
  accurate quality, a small Swift script beside it), crops face and hair to a square,
  stretches contrast inside the mask (`autocontrast` 2%/1% cutoffs, `UnsharpMask(8, 220,
  1)`, gamma 1.7), and writes **`data/portrait.json`**: a 42 × 66 brightness grid, two
  decimals. The photo never enters the repo. For the 1500 × 2000 photo the approved crop
  is `(300, 120, 1150, 970)`; scale it for other sizes.
- **`tools/neofetch.py`** draws the card from that grid. The jitter is seeded, so the
  daily redraw is deterministic and the portrait never causes a diff. The ramp is
  ` .,:;i1tfLCG08@`. Glyphs are drawn once as symbols and placed with `<use>`, as today.
- **Assets:** `assets/card.svg` and `assets/card-narrow.svg`. The four themed
  `card-{light,dark}{,-narrow}.svg` go; the README drops its theme sources.
- **README alt text:** "Nihan Bayrak as a moving terminal readout: her portrait drawn in
  signs beside her details. Berlin." No company.
- **`CLAUDE.md`** names "Direction B, editorial" (paper, near-black, oxblood) as the
  design and the four themed cards as the output. Update both to this document.
- **Dependencies:** the nightly job installs only `fonttools` and `uharfbuzz`. Seed the
  jitter with the standard library's `random`, not numpy, so it needs nothing new.
  `portrait.py` runs only on her Mac and may use numpy and Pillow.
- **Workflow:** `refresh.yml` keeps its schedule and pinned versions. Nothing to carry
  over from `fix-workflow-deps`: it is already in `main`'s history, and the `skia-pathops`
  it added served `tools/sort3d.py`, which is not on `main`.

### Size

Eight frames of 66 × 42 signs is about 22,000 `<use>` elements. Keep each card under
**1 MB**: skip spaces, round coordinates, share symbols. If it will not fit, drop to 6
frames before shrinking the grid; the face matters more than the frame count.

## The reference, kept beside this document

`2026-11-22-living-card/` holds what the approval was given on, because the scratch folder
it was made in has already been wiped once:

- `approved-mockup.html`: the approved A1, final words. Open it in a browser to compare.
- `portrait-reference.json`: the approved face as a 42 × 66 brightness grid. **The source
  of truth for the portrait.** If her photo is not to hand, build from this grid; do not
  ask her for the photo again. `data/portrait.json` should equal it.
- `mockup.py`: the generator. Wide-card metrics not written above come from here (signs
  8.6 px on a 9.2 px row pitch from x 20, y 22; readout at x 384 from y 40 on 22 px
  leading; motto baseline y 372), and so do the portrait details: the mask clamp
  `(m − 0.45) / 0.25` that drops people behind her, the mask > 140 used for autocontrast,
  BOX resampling, and the 0.02 cutoff before jitter.
- `live_check.py` and `segment.swift`: the playback harness and the cut-out.

The `.gitignore` there keeps her photo out if `mockup.py` is ever rerun in that folder.

## How to know it works

The mockup harness (Playwright driving the Mac's own Chrome, headless so it is never
throttled) proved the approved behaviour. Rebuild it as a check the repo keeps:

1. Play `assets/card.svg` for 8 s; on every animation frame exactly **one** portrait frame
   is at opacity 1, and at most **one** motto mask is open.
2. Screenshots every ~250 ms: none blank in the portrait area.
3. Seek each motto: every typing step's mask edge lands within 0.6 px of a glyph boundary,
   the step count equals the character count, and the held edge covers the whole line.
4. `grep` the asset for `<text` and `@font-face`: none.
5. File size under 1 MB.
6. Look at it, in a browser, beside the approved mockup: the face matches.

### Done means: a preview branch on GitHub

Nihan's call, 22 Nov. When every check above passes on the Mac, push the work to a
**preview branch** (not `main`) and view its README on github.com, light and dark, wide
and narrow. That push is the one she has approved; `main` is a separate decision she makes
after seeing the preview. Rebase onto `origin/main` right before pushing: the nightly bot
keeps committing to the themed cards this branch deletes.

`refresh.yml` does not run on a preview branch, so the nightly job (Fraunces in
`tools/fonts/`, no numpy) is first exercised when she merges. Run `tools/stats.py` and
`tools/neofetch.py` once locally with only the workflow's pinned packages installed,
to stand in for it.

## Left to the builder

The narrow layout's exact metrics, symbol and id naming, how the check is wired (script or
test), and any size trimming within the rules above.

## Her side (not code)

Things only Nihan can do on github.com, listed so the build can point at them:
- Make `nihanbayrak/nihanbayrak` public; GitHub shows nothing while it is private.
- Clear "WIN CREATING IMAGES" from the company field; write a personal bio.
- Pin `llm-copyright-judge-eval` first; give `pipelinexpert` a description or unpin it.
- Nothing is pushed without her say-so.
