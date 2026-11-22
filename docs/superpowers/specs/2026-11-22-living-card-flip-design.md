# The living card, flipped and steadier: design

22 Nov 2026. A small change to the living card
(`2026-11-22-living-card-design.md`), from Nihan's review of full-page mockups. Goes into
PR #8 before it merges.

## What and why

- **Flip the wide card.** The readout on the left, her face on the right. She picked this
  ("B") from three full-profile mockups: her real photo sits in the sidebar on the left, so
  the card's face on the far right balances the page, and the readout comes right after her
  name and bio.
- **Remove the glitch.** Frames 3 and 6 slid a band of three rows sideways. On the page it
  read as the portrait "flipping". The shimmer stays: every frame still re-inks the signs.

## Approaches

- **Flip:** move the two columns (chosen), or mirror the portrait. Mirroring would change
  her face, which the spec forbids; moving keeps every sign exactly as approved.
- **Glitch:** drop it entirely (chosen), or make it rarer or smaller. She asked for it
  gone.

## The change

- Wide card, 830 × 420: readout and mottos at x 24 (readout from y 40, mottos baseline
  y 372, as before); portrait at x 470. 52 readout columns at 12 px end at x 398; the
  portrait's 66 columns at 8.6 px end at x 811. Nothing else moves.
- The narrow card stays stacked as it is (portrait on top, then readout, then the motto).
  *(My call: on a phone there is no side to flip.)*
- `motion.frames` no longer shifts any band. The 8 frames keep their own jitter, so the
  shimmer is unchanged.

## Must still hold

Every rule of the main spec: one frame visible at any moment, letters typed whole, one
motto at a time, complete at rest, no `<text>`, under 1 MB, byte-identical redraws, the face
equal to `portrait-reference.json`. The mottos' mask now pivots at x 24.

## Left to the builder

Nothing beyond the numbers above.
