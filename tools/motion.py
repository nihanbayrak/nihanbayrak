"""Every rule the card moves by, as plain functions, so it can be tested without a browser.

The portrait is a flipbook: eight frames of the same face, re-inked with fresh jitter so
the signs shimmer; frames 3 and 6 also slide a three-row band sideways, a signal glitch.
The mottos type out under a mask that steps from one letter's right edge to the next.

Two rules here were wrong in the first mockup and are the reason this file exists:

- **One shared cycle for the frames.** Every frame runs the same step-end animation with
  no delay, and frame k's window is written into its own keyframes. Frame k going off
  and frame k+1 coming on are the same keyframe value, so exactly one frame is ever
  visible. Eight animations timed with staggered delays left gaps where the face blinked.
- **Measured letter edges.** The mask steps to HarfBuzz's right edge of each letter
  (typeset.advances), not to an average width, so no letter ever shows cut in half.
"""
import random
import re

RAMP = " .,:;i1tfLCG08@"
N_FRAMES = 8
FLIP_S = 1.6
CYCLE_S = 18
GLITCH = (3, 6)
TYPE_END, HOLD_END, ERASE_END = 12, 28, 32     # percent of the motto loop


def _pct(x):
    return f"{x:.4f}%"


def frames(grid, seed=11):
    """N_FRAMES frames, each a list of rows of signs, one per cell of `grid`."""
    rng = random.Random(seed)
    rows, cols = len(grid), len(grid[0])
    out = []
    for k in range(N_FRAMES):
        lines = []
        for r in range(rows):
            signs = []
            for c in range(cols):
                b = grid[r][c]
                v = min(1.0, max(0.0, b + rng.uniform(-0.09, 0.09))) if b > 0.02 else 0.0
                signs.append(RAMP[int(v * (len(RAMP) - 1) + 0.5)])
            lines.append("".join(signs))
        if k in GLITCH:
            r0, shift = rng.randrange(8, rows - 8), rng.choice((-3, -2, 2, 3))
            for r in range(r0, r0 + 3):
                lines[r] = lines[r][-shift:] + lines[r][:-shift]
        out.append(lines)
    return out


def flip_css(prefix):
    """Keyframes and classes {prefix}f0 … {prefix}f7: frame k shows from k/8 to (k+1)/8."""
    css = []
    for k in range(N_FRAMES):
        on, off = _pct(100 * k / N_FRAMES), _pct(100 * (k + 1) / N_FRAMES)
        if k == 0:
            kf = f"0%{{opacity:1}}{off}{{opacity:0}}100%{{opacity:0}}"
        elif k == N_FRAMES - 1:
            kf = f"0%{{opacity:0}}{on}{{opacity:1}}100%{{opacity:1}}"
        else:
            kf = f"0%{{opacity:0}}{on}{{opacity:1}}{off}{{opacity:0}}100%{{opacity:0}}"
        # at rest, where animation does not run, only frame 0 shows
        rest = "opacity:0;" if k else ""
        css.append(f"@keyframes {prefix}f{k}{{{kf}}}"
                   f".{prefix}f{k}{{{rest}animation:{prefix}f{k} {FLIP_S}s step-end infinite}}")
    return "".join(css)


def type_css(prefix, j, edges, width, x=0):
    """Keyframes and class {prefix}v{j} for motto j's mask rect.

    `edges` are the mask's right edge after 0, 1, … n letters (edges[0] == 0); `width` is
    the rect's width and `x` its left edge, in user units. Type to TYPE_END, hold to
    HOLD_END, erase by ERASE_END, then hide.

    The rect scales from its own left edge, written in user units: that needs no
    transform-box, which not every engine honours. At rest — where animation does not
    run — motto 0 shows in full and the others stay hidden.
    """
    n = len(edges) - 1
    steps = [(TYPE_END * i / n, edges[i]) for i in range(n + 1)]
    steps += [(HOLD_END + (ERASE_END - HOLD_END) * (n - i) / n, edges[i]) for i in range(n, -1, -1)]
    kf = "".join(f"{_pct(t)}{{transform:scaleX({e / width:.4f})}}" for t, e in steps)
    kf += "100%{transform:scaleX(0)}"
    delay = -CYCLE_S + j * CYCLE_S // 3
    return (f"@keyframes {prefix}v{j}{{{kf}}}"
            f".{prefix}v{j}{{transform-origin:{x:g}px 0;transform:scaleX({1 if j == 0 else 0});"
            f"animation:{prefix}v{j} {CYCLE_S}s step-end {delay}s infinite}}")


def still_css(prefix):
    """Under reduced motion: frame 0 and motto 0, complete and still."""
    hide = ",".join(f".{prefix}f{k}" for k in range(1, N_FRAMES))
    return ("@media (prefers-reduced-motion: reduce){"
            f".{prefix}f0,{hide},.{prefix}v0,.{prefix}v1,.{prefix}v2{{animation:none}}"
            f".{prefix}f0{{opacity:1}}{hide}{{opacity:0}}"
            f".{prefix}v0{{transform:scaleX(1)}}.{prefix}v1,.{prefix}v2{{transform:scaleX(0)}}}}")


# ---------------------------------------------------------------- reading it back

def _keyframes(css, name):
    body = re.search(r"@keyframes " + re.escape(name) + r"\{((?:[^{}]*\{[^{}]*\})*)\}", css).group(1)
    return [(float(p.rstrip("%")), decl) for p, decl in re.findall(r"([\d.]+%)\{([^{}]*)\}", body)]


def _at(frames_, progress):
    """step-end: the value of the last keyframe at or before `progress` (0..1)."""
    value = frames_[0][1]
    for p, decl in frames_:
        if p / 100 <= progress + 1e-12:
            value = decl
    return value


def visible_frames(css, progress):
    """Which frames are at opacity 1 at `progress` (0..1) of the flip cycle."""
    prefix = re.search(r"@keyframes (\w+?)f0\{", css).group(1)
    return [k for k in range(N_FRAMES)
            if _at(_keyframes(css, f"{prefix}f{k}"), progress) == "opacity:1"]


def mask_scale(css, j, progress):
    """Motto j's mask scaleX at `progress` (0..1) of that motto's own loop."""
    prefix = re.search(r"@keyframes (\w+?)v\d\{", css).group(1)
    decl = _at(_keyframes(css, f"{prefix}v{j}"), progress)
    return float(re.search(r"scaleX\(([\d.]+)\)", decl).group(1))
