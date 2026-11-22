# The living card, readout v2: design

22 Nov 2026. A copy change to the living card (`2026-11-22-living-card-design.md`), from
Nihan's own list. She approved this exact layout in a text preview.

## The readout

```
nihan@bayrak ──────────────────────────────────────────────────────
─ Profile ─────────────────────────────────────────────────────────
role ................ AI specialist
dayJob .............. AI tools for consumer brands
city ................ Berlin
spokenLanguages ..... TR, EN, DE
uptime .............. 9 years, 1 month, 27 days          ← live

tools.languages ..... Python, TypeScript, SQL
tools.ide ........... Claude Code, Xcode, Codex, VS Code, Langdock
tools.shell ......... zsh

interests.creative .. 3D modeling and printing
interests.offScreen . Modeling, sailing, creating gifts

─ Projects ────────────────────────────────────────────────────────
evals ............... Copyright risk in image prompts
agents .............. Roundtrip · TestFlight feedback triage
product ............. Conscious Eyes · iOS label scanner

─ Contact ─────────────────────────────────────────────────────────
linkedIn ............ nihan-bayrak
website ............. consciouseyes.app

─ GitHub ──────────────────────────────────────────────────────────
commits ............. 444 · repos 17 · followers 28      ← live
```

Her words, verbatim, except `uptime` and the GitHub line, which she chose to keep because
they are what the nightly redraw updates. Keys are her camelCase names.

## Layout (my calls)

- A pair is `key + " " + "." * (20 - len(key)) + " " + value`, so values start at column 22;
  the widest line (`tools.ide`) is 66 columns. Rules run the full 66 columns.
- Wide card: readout JetBrains Mono 11 px (66 columns = 436 px, from x 24 to x 460; the
  portrait stays at x 470), leading 16 px, 26 rows. The card grows to 830 × 520; the portrait
  is centred vertically; the motto sits under the readout.
- Narrow card: readout size chosen so 66 columns fit its width; still stacked.
- Everything else in the main spec still holds.
