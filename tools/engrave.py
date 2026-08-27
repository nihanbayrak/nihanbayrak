"""Turning a mesh into an engraving.

A README allows no JavaScript and no WebGL, so the turn is a zoetrope: a fixed
number of orthographic projections cycled by CSS.

The projections are not drawn as polygons. Forty-eight frames of a real mesh
would run to megabytes of path data, and flat-shaded facets look like a 1996
screensaver besides. Each frame is rasterised properly -- z-buffer, one lamp --
and the resulting tone is then cut as line work: parallel lines at a fixed angle
whose weight carries the shading, exactly the way a copperplate engraver builds
a tone. Output size scales with the number of hatch lines, not with the mesh.

The hatching belongs to the plate, not to the object, so it does not turn with it.
"""
import math

import numpy as np

GROUND = "#F5F1E8"
INK = "#1A1611"
ACC = "#8B2027"

FRAMES = 40
TURN = 5.0                       # seconds per revolution -- 8fps, a zoetrope
TILT = math.radians(11)          # a shade above eye level
LIGHT = np.array([-0.72, 0.46, 0.52])   # lateral, not a headlight -- a dome needs a side
LIGHT = LIGHT / np.linalg.norm(LIGHT)

SS = 2                           # raster samples per svg unit
HATCH = math.radians(-34)        # the plate's screen angle
GAP = 6.2                        # svg units between hatch lines
LEVELS = ((0.82, 0.50), (0.62, 0.85), (0.40, 1.20), (0.19, 1.60))
CROSS = math.radians(56)         # second pass, darkest tone only


def camera(v, theta, tilt=TILT):
    c, s = math.cos(theta), math.sin(theta)
    x = v[:, 0] * c + v[:, 2] * s
    z = -v[:, 0] * s + v[:, 2] * c
    ct, st = math.cos(tilt), math.sin(tilt)
    return np.stack([x, v[:, 1] * ct - z * st, v[:, 1] * st + z * ct], axis=1)


# ---------------------------------------------------------------- raster

def _raster(P, f, accent, w, h, scale, cx, cy):
    """Z-buffer the frame. Returns tone, depth and the mask of what prints red."""
    sx = cx + P[:, 0] * scale
    sy = cy - P[:, 1] * scale

    a, b, c = f[:, 0], f[:, 1], f[:, 2]
    ax, ay, az = sx[a], sy[a], P[a, 2]
    bx, by, bz = sx[b], sy[b], P[b, 2]
    cx_, cy_, cz = sx[c], sy[c], P[c, 2]

    # Normals come from camera space, not from the projected pixels: screen x and
    # y are scaled by several hundred and z is not, so a cross product taken over
    # there has a meaningless z and lights the model almost uniformly.
    n = np.cross(P[b] - P[a], P[c] - P[a])
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1e-9
    n /= ln[:, None]
    # Winding is not to be trusted across 427 separate parts, but whatever the
    # z-buffer keeps is by definition the surface facing the viewer -- so turn
    # every normal to face the camera and light it one-sided from there.
    n *= np.where(n[:, 2] < 0, -1.0, 1.0)[:, None]
    lam = np.maximum(0.0, n @ LIGHT)
    tone_of = 0.11 + 0.89 * lam

    # sum of the three edge functions is twice the signed area, constant per triangle
    ar = (bx - ax) * (cy_ - ay) - (by - ay) * (cx_ - ax)

    x0 = np.clip(np.floor(np.minimum(np.minimum(ax, bx), cx_)).astype(int), 0, w - 1)
    x1 = np.clip(np.ceil(np.maximum(np.maximum(ax, bx), cx_)).astype(int), 0, w - 1)
    y0 = np.clip(np.floor(np.minimum(np.minimum(ay, by), cy_)).astype(int), 0, h - 1)
    y1 = np.clip(np.ceil(np.maximum(np.maximum(ay, by), cy_)).astype(int), 0, h - 1)

    zbuf = np.full((h, w), -1e30)
    tone = np.ones((h, w))
    hot = np.zeros((h, w), dtype=bool)

    for i in range(len(f)):
        xa, xb = x0[i], x1[i]
        ya, yb = y0[i], y1[i]
        if xb < xa or yb < ya:
            continue
        gx = np.arange(xa, xb + 1) + 0.5
        gy = (np.arange(ya, yb + 1) + 0.5)[:, None]

        w0 = (bx[i] - ax[i]) * (gy - ay[i]) - (by[i] - ay[i]) * (gx - ax[i])
        w1 = (cx_[i] - bx[i]) * (gy - by[i]) - (cy_[i] - by[i]) * (gx - bx[i])
        w2 = (ax[i] - cx_[i]) * (gy - cy_[i]) - (ay[i] - cy_[i]) * (gx - cx_[i])
        area = ar[i]
        if area == 0:
            continue
        inside = ((w0 >= 0) & (w1 >= 0) & (w2 >= 0)) | ((w0 <= 0) & (w1 <= 0) & (w2 <= 0))
        if not inside.any():
            continue
        z = (w0 * cz[i] + w1 * az[i] + w2 * bz[i]) / area

        sl = (slice(ya, yb + 1), slice(xa, xb + 1))
        win = inside & (z > zbuf[sl])
        if not win.any():
            continue
        zbuf[sl] = np.where(win, z, zbuf[sl])
        tone[sl] = np.where(win, tone_of[i], tone[sl])
        hot[sl] = np.where(win, accent[i], hot[sl])

    mask = zbuf > -1e29

    # creases: where the surface jumps away from itself, an engraver cuts deeper
    z = np.where(mask, zbuf, np.nan)
    step = np.zeros_like(tone)
    for dy, dx in ((0, 1), (1, 0)):
        d = np.abs(np.roll(z, (dy, dx), (0, 1)) - z)
        step = np.fmax(step, np.nan_to_num(d))
    # a one-pixel crease falls between hatch lines and prints as nothing, so
    # widen it until the engraver's lines actually cross it
    cut = step > 0.014
    for _ in range(2):
        cut = (cut | np.roll(cut, 1, 0) | np.roll(cut, -1, 0)
               | np.roll(cut, 1, 1) | np.roll(cut, -1, 1))
    tone = np.where(cut & mask, tone * 0.42, tone)

    # Facet noise makes a hatch line flicker between weights and break into
    # dozens of stubs -- costly on disk and scratchy on the page. Average the
    # tone across its own neighbours only, so the silhouette stays sharp.
    num = np.where(mask, tone, 0.0)
    den = mask.astype(float)
    for _ in range(2):
        n2, d2 = num.copy(), den.copy()
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            n2 += np.roll(num, (dy, dx), (0, 1))
            d2 += np.roll(den, (dy, dx), (0, 1))
        num, den = n2, d2
        num, den = num / 5, den / 5
    tone = np.where(mask & (den > 0), num / np.maximum(den, 1e-9), tone)
    return tone, mask, hot


# ---------------------------------------------------------------- tracing

def _loops(mask):
    """Boundary of a raster region as closed loops, wound clockwise on screen."""
    h, w = mask.shape
    pad = np.zeros((h + 2, w + 2), dtype=bool)
    pad[1:-1, 1:-1] = mask
    m = pad[1:-1, 1:-1]

    seg = {}

    def add(ys, xs, p, q):
        for y, x in zip(ys, xs):
            seg.setdefault((x + p[0], y + p[1]), []).append((x + q[0], y + q[1]))

    add(*np.nonzero(m & ~pad[1:-1, :-2]), (0, 1), (0, 0))        # empty to the left
    add(*np.nonzero(m & ~pad[:-2, 1:-1]), (0, 0), (1, 0))        # empty above
    add(*np.nonzero(m & ~pad[1:-1, 2:]), (1, 0), (1, 1))         # empty to the right
    add(*np.nonzero(m & ~pad[2:, 1:-1]), (1, 1), (0, 1))         # empty below

    out = []
    while seg:
        start = next(iter(seg))
        loop, node = [start], start
        while True:
            nxt = seg.get(node)
            if not nxt:
                break
            step = nxt.pop()
            if not nxt:
                del seg[node]
            node = step
            if node == start:
                break
            loop.append(node)
        if len(loop) > 7:
            out.append(loop)
    return out


def _rdp(pts, tol):
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy) or 1e-9
        worst, wi = -1.0, a
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / norm
            if d > worst:
                worst, wi = d, i
        if worst > tol:
            keep[wi] = True
            stack += [(a, wi), (wi, b)]
    return [p for p, k in zip(pts, keep) if k]


def _smooth_loop(loop, tol):
    """Douglas-Peucker around a closed ring, cut at its two furthest anchors."""
    n = len(loop)
    if n < 10:
        return loop
    a = min(range(n), key=lambda i: loop[i])
    b = max(range(n), key=lambda i: (loop[i][0] - loop[a][0]) ** 2
                                    + (loop[i][1] - loop[a][1]) ** 2)
    a, b = min(a, b), max(a, b)
    out = _rdp(loop[a:b + 1], tol)[:-1] + _rdp(loop[b:] + loop[:a + 1], tol)[:-1]
    return out if len(out) >= 3 else loop


def _area(poly):
    a = 0.0
    for i, (x, y) in enumerate(poly):
        x2, y2 = poly[(i + 1) % len(poly)]
        a += x * y2 - x2 * y
    return abs(a) / 2


def _i(v):
    return str(int(round(v)))


def _n(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def _path(loops, ox, oy):
    out = []
    for lp in loops:
        pts = [(x / SS + ox, y / SS + oy) for x, y in lp]
        out.append("M" + "L".join(f"{_n(x)} {_n(y)}" for x, y in pts) + "Z")
    return "".join(out)


def _outline(mask, ox, oy, tol=1.7, floor=14):
    loops = [_smooth_loop(lp, tol) for lp in _loops(mask)]
    return _path([lp for lp in loops if _area(lp) > floor], ox, oy)


# ---------------------------------------------------------------- hatching

def _hatch(tone, mask, angle, ox, oy, levels, gap=GAP):
    """Cut one pass of parallel lines. Weight, not spacing, carries the tone."""
    h, w = tone.shape
    dx, dy = math.cos(angle), math.sin(angle)
    nx, ny = -dy, dx
    span = int(math.hypot(w, h) / 2) + 2
    step = gap * SS

    cxp, cyp = w / 2, h / 2
    runs = [[] for _ in levels]
    cuts = np.array([lv[0] for lv in levels])

    k = -int(span / step) - 1
    while k * step <= span:
        bx, by = cxp + nx * k * step, cyp + ny * k * step
        k += 1
        t = np.arange(-span, span, 1.0)
        px = bx + dx * t
        py = by + dy * t
        ok = (px >= 0) & (px < w) & (py >= 0) & (py < h)
        if not ok.any():
            continue
        t, px, py = t[ok], px[ok], py[ok]
        xi, yi = px.astype(int), py.astype(int)

        lv = np.where(mask[yi, xi], np.searchsorted(-cuts, -tone[yi, xi]), 0)
        if not lv.any():
            continue

        # one run per stretch of constant weight
        brk = np.nonzero(np.diff(lv))[0]
        starts = np.concatenate(([0], brk + 1))
        ends = np.concatenate((brk, [len(lv) - 1]))
        for s0, s1 in zip(starts, ends):
            level = int(lv[s0])
            if level == 0 or s1 - s0 < 3:      # shorter than the line is wide
                continue
            # whole units: a quarter of a percent of the plate, and a third of
            # the bytes -- the ragged ends read as bite, not as error
            runs[level - 1].append(
                f"M{_i(px[s0] / SS + ox)} {_i(py[s0] / SS + oy)}"
                f"L{_i(px[s1] / SS + ox)} {_i(py[s1] / SS + oy)}")
    return runs


# ---------------------------------------------------------------- the plate

class Engraver:
    def __init__(self, v, f, accent, box, tilt=TILT, frames=FRAMES):
        self.v, self.f, self.accent = v, f, accent
        self.tilt, self.frames = tilt, frames

        bx, by, bw, bh = box
        xs, ys = [], []
        for i in range(frames):
            P = camera(v, math.tau * i / frames, tilt)
            xs += [P[:, 0].min(), P[:, 0].max()]
            ys += [P[:, 1].min(), P[:, 1].max()]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        self.scale = min(bw / (x1 - x0), bh / (y1 - y0))
        self.ox = bx + bw / 2 - (x0 + x1) / 2 * self.scale
        self.oy = by + bh / 2 + (y0 + y1) / 2 * self.scale

        self.w = int(bw * SS) + 2
        self.h = int(bh * SS) + 2
        self.px = (self.ox - bx) * SS
        self.py = (self.oy - by) * SS
        self.bx, self.by = bx, by

    def frame(self, theta):
        P = camera(self.v, theta, self.tilt)
        tone, mask, hot = _raster(P, self.f, self.accent, self.w, self.h,
                                  self.scale * SS, self.px, self.py)
        ox, oy = self.bx, self.by

        # No paper fill under the object: the card's grain should read straight
        # through it, and the fill was a third of every frame's bytes.
        body = []

        runs = _hatch(tone, mask, HATCH, ox, oy, LEVELS)
        dark = _hatch(tone, mask & (tone < LEVELS[-1][0]), CROSS, ox, oy, LEVELS[-1:])
        for (_, width), d in zip(LEVELS, runs):
            if d:
                body.append(f'<path d="{"".join(d)}" fill="none" stroke="{INK}"'
                            f' stroke-width="{width}" stroke-linecap="round"/>')
        if dark[0]:
            body.append(f'<path d="{"".join(dark[0])}" fill="none" stroke="{INK}"'
                        f' stroke-width="{LEVELS[-1][1] * 0.8:.2f}" stroke-linecap="round"/>')

        body.append(f'<path d="{_outline(mask, ox, oy)}" fill="none" stroke="{INK}"'
                    f' stroke-width="1.15" stroke-linejoin="round"/>')

        if hot.any():
            d = _outline(hot, ox, oy, tol=1.2, floor=6)
            if d:
                body.append(f'<path d="{d}" fill="{ACC}" fill-rule="evenodd"'
                            f' stroke="{ACC}" stroke-width=".7"/>')
        return "".join(body)

    def plate(self):
        step = TURN / self.frames
        out = []
        for i in range(self.frames):
            delay = -((self.frames - i) % self.frames) * step
            out.append(f'<g class="fr" style="animation-delay:{delay:.3f}s">'
                       + self.frame(math.tau * i / self.frames) + '</g>')
        return "".join(out)


STYLE = (f"  .fr {{ opacity:0; animation:zoe {TURN}s linear infinite }}\n"
         f"  @keyframes zoe {{ 0%,{100/FRAMES - 0.05:.3f}% {{ opacity:1 }}"
         f" {100/FRAMES:.3f}%,100% {{ opacity:0 }} }}\n")
