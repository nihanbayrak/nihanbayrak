"""The octopus, swimming: the mesh is bent frame by frame instead of only turned.

The dome is held rigid. Everything else bends with its distance from the collar,
so the arms move more the further out they reach: a travelling wave runs down
each arm, out of step with its neighbours, the arms open and close in two
strokes a loop, the body rides up on each stroke, and the whole animal turns a
little to one side and back so the depth shows. Every term is periodic in the
loop, so the last frame meets the first.

The renderer is shade.py, untouched in its rules; this only hands it bent
vertices, fresh normals and a bent shadow mesh for each frame.
"""
import math

import numpy as np

import model3d

COLLAR_Y, COLLAR_R = 0.58, 0.12          # where the arms leave the body (normalised model)
CORE_Y, CORE_R = 0.56, 0.18              # the dome and its cage, held rigid

STROKES = 2                              # strokes per loop
WAVE = 7.0                               # how many radians the wave turns along an arm
TURN = 0.45                              # radians either side of facing


def _bend(v, phase):
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    r = np.hypot(x, z)
    ang = np.arctan2(z, x)
    reach = np.hypot(np.maximum(r - COLLAR_R, 0), y - COLLAR_Y)   # roughly, along the arm
    w = np.clip(reach / 0.75, 0, 1)
    w[(y > CORE_Y) & (r < CORE_R)] = 0

    s = math.tau * STROKES * phase
    travel = s - WAVE * reach + 3 * ang          # each arm a little out of step
    r2 = r * (1 + 0.09 * w * math.sin(s))                           # open and close
    a2 = ang + 0.06 * w ** 1.4 * np.sin(travel) / np.maximum(r, 0.05)  # sideways wave
    y2 = y + 0.04 * w * np.sin(travel + math.pi / 2) + 0.025 * math.cos(s)  # wave, and the body rides
    out = np.stack([r2 * np.cos(a2), y2, r2 * np.sin(a2)], axis=1)
    return out


def frames(sh, n):
    """Yield (rgb, alpha) for n frames of one loop. Restores the shader after."""
    v0, sv0, n0 = sh.v, sh.sv, sh.n
    try:
        for i in range(n):
            phase = i / n
            sh.v = _bend(v0, phase)
            sh.n = model3d.vertex_normals(sh.v, sh.f)
            sh.sv = _bend(sv0, phase)
            yield sh.frame(TURN * math.sin(math.tau * phase), background=True)
    finally:
        sh.v, sh.sv, sh.n = v0, sv0, n0
