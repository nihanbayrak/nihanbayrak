# Living Card Flip Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Flip the wide card (readout left, face right) and remove the portrait's sideways glitch.

**Architecture:** Two edits to the existing pipeline: `motion.frames` stops shifting bands; `neofetch.build` swaps the wide card's column positions. Everything else is unchanged.

**Tech Stack:** Python 3.12, stdlib `unittest`, Playwright + Chrome for the playback check.

**Spec:** `docs/superpowers/specs/2026-11-22-living-card-flip-design.md` (amends `2026-11-22-living-card-design.md`).

## Global Constraints

- Worktree `~/claude_workspace/github-profile-living-card`, branch `living-card` (PR #8). Python `../github-profile/.venv/bin/python`.
- Wide card: readout and mottos at x 24 (readout from y 40, motto baseline y 372); portrait at x 470. Narrow card unchanged.
- Every main-spec rule still holds (one frame at a time, letters whole, one motto at a time, complete at rest, no `<text>`, < 1 MB, deterministic, face = reference grid).

## Review Focus

1. **Columns colliding.** The readout's 52 columns and the longest motto must end left of the portrait at x 470. Test in Task 2.
2. **The face moved, not changed.** Every portrait frame must be the unflipped frame translated by 450 px, nothing else. Test in Task 2.
3. **The narrow card.** It must be byte-identical to before apart from the glitch frames. Checked in Task 2 by rebuilding.

---

### Task 1: No glitch

**Files:** Modify `tools/motion.py` (drop `GLITCH` and the band shift in `frames`); Test `tests/test_motion.py`.

- [ ] **Step 1: Replace `test_frames_deterministic_and_glitch_only_on_3_and_6` with `test_frames_deterministic_and_steady`:** frames equal across two calls, 8 × 42 × 66, and for every frame and every cell where `GRID[r][c] == 0` the sign is `" "`.
- [ ] **Step 2: Run it.** Expected: FAIL on frames 3 and 6.
- [ ] **Step 3: Remove the band shift and `GLITCH` from `motion.py`; update its docstring.**
- [ ] **Step 4: Run the suite.** Expected: all PASS.
- [ ] **Step 5: Commit** `tools/motion.py tests/test_motion.py`.

### Task 2: Flip the wide card

**Files:** Modify `tools/neofetch.py:172-173`; Test `tests/test_card.py`; regenerate `assets/card.svg`, `assets/card-narrow.svg`.

- [ ] **Step 1: Write `test_wide_card_is_flipped`:** the wide SVG contains `translate(470.0 ` (portrait) and `translate(24.0 ` (readout) and `translate(24.00 ` (motto) and `x="24"` and `transform-origin:24px 0`, and no `translate(384.`; and `24 + neofetch.Mono().width(52, 12) < 470` and `24 + max(typeset.measure(m, "voice", 19) for m in MOTTOS) < 470`.
- [ ] **Step 2: Run it.** Expected: FAIL.
- [ ] **Step 3: Set `art_x, info_x = 470, 24` and `voice_x = 24` for the wide card.**
- [ ] **Step 4: Run the suite, regenerate both cards, run `tools/check_live.py`.** Expected: all PASS; both cards < 977 KB; check_live PASS.
- [ ] **Step 5: Commit** code, test and both cards; push `living-card` (PR #8).
