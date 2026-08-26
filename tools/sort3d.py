"""A piece of foundry type, turning.

The equivalent object for this page is not a person. The README's whole argument
is that it typesets itself, so the object is a sort: a piece of foundry type,
cast with the letter reversed the way type actually is, turning once every four
seconds.

There is no WebGL in a README and no JavaScript, so the rotation is a zoetrope --
48 orthographic projections cycled by CSS. Shading is engraved rather than
smooth: five hatch densities in fixed plate space, which is how an engraver would
have printed a turning object anyway. The hatching belongs to the plate, not to
the object, so it does not rotate with it.

Geometry conventions: x right, y up, z toward the viewer. Every ring runs
counter-clockwise in the (x, z) plane, which makes the stitched quads
outward-facing without any winding guesswork.
"""
import math

import pathops
import typeset as T
from fontTools.pens.basePen import BasePen

GROUND = "#F5F1E8"
INK = "#1A1611"
ACC = "#8B2027"

FRAMES = 48
TURN = 4.0                      # seconds per revolution -- 12fps, zoetrope cadence
TILT = math.radians(26)         # looking down onto the face
LIGHT = (-0.44, 0.60, 0.67)     # one lamp, upper left, fixed to the plate

GLYPH = "N"
FACE = "display"                # Cormorant Infant Light, same as the banner name

HB = 1.34                       # shank height, in cap-heights
RELIEF = 0.105                  # how far the letter stands off the face


# ---------------------------------------------------------------- outlines

class _FlattenPen(BasePen):
    """Glyph outline as polygons. Curves become segments; 3D wants points."""

    def __init__(self, glyphset, steps=7):
        super().__init__(glyphset)
        self.contours, self._cur, self.steps = [], None, steps

    def _moveTo(self, pt):
        self._flush()
        self._cur = [pt]

    def _lineTo(self, pt):
        self._cur.append(pt)

    def _curveToOne(self, p1, p2, p3):
        p0 = self._cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            s = 1 - t
            self._cur.append((
                s*s*s*p0[0] + 3*s*s*t*p1[0] + 3*s*t*t*p2[0] + t*t*t*p3[0],
                s*s*s*p0[1] + 3*s*s*t*p1[1] + 3*s*t*t*p2[1] + t*t*t*p3[1],
            ))

    def _closePath(self):
        self._flush()

    def _endPath(self):
        self._flush()

    def _flush(self):
        c = self._cur
        self._cur = None
        if not c or len(c) < 3:
            return
        if abs(c[0][0] - c[-1][0]) < 1e-6 and abs(c[0][1] - c[-1][1]) < 1e-6:
            c = c[:-1]
        self.contours.append(c)


def _area(poly):
    a = 0.0
    for i, (u, v) in enumerate(poly):
        u2, v2 = poly[(i + 1) % len(poly)]
        a += u * v2 - u2 * v
    return a / 2


def _rdp_open(pts, tol):
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


def _rdp(poly, tol):
    """Douglas-Peucker on a closed contour.

    Cut the loop at its two furthest-apart anchors first. Run end to end and the
    opening span is degenerate -- every point measures zero off it, nothing ever
    splits, and the whole contour comes back unsimplified.
    """
    n = len(poly)
    if n < 8:
        return poly
    a = min(range(n), key=lambda i: (poly[i][0], poly[i][1]))
    b = max(range(n), key=lambda i: (poly[i][0] - poly[a][0]) ** 2
                                    + (poly[i][1] - poly[a][1]) ** 2)
    a, b = min(a, b), max(a, b)
    out = _rdp_open(poly[a:b + 1], tol)[:-1] + _rdp_open(poly[b:] + poly[:a + 1], tol)[:-1]
    return out if len(out) >= 3 else poly


def letter_plan():
    """The glyph on the top face: (x, z) polygons, cap height 1.0, mirrored as cast."""
    tt, glyphset, _, _ = T._load(FACE)

    # Cormorant draws N as three overlapping pieces. Union them before extruding,
    # or every join becomes a wall buried inside the solid, drawn but meaningless.
    path = pathops.Path()
    glyphset[tt.getBestCmap()[ord(GLYPH)]].draw(path.getPen(glyphSet=glyphset))
    path.simplify(fix_winding=True)

    pen = _FlattenPen(glyphset)
    path.draw(pen)

    xs = [p[0] for c in pen.contours for p in c]
    ys = [p[1] for c in pen.contours for p in c]
    s = 1.0 / (max(ys) - min(ys))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2

    # Font x runs to screen left (the letter is cut in reverse), font y runs away
    # from the viewer across the face.
    plan = [_rdp([(-(x - cx) * s, -(y - cy) * s) for x, y in c], 0.005)
            for c in pen.contours]

    areas = [_area(c) for c in plan]
    outer = max(range(len(areas)), key=lambda i: abs(areas[i]))
    if areas[outer] < 0:                       # outer contour must run CCW
        plan = [c[::-1] for c in plan]
    return plan


# ---------------------------------------------------------------- mesh

def _ring(w, d, y, inset=0.0, nick=0.0):
    hw, hd = w / 2 - inset, d / 2 - inset
    return [(hw, y, hd - nick), (-hw, y, hd - nick), (-hw, y, -hd), (hw, y, -hd)]


def _newell(pts):
    nx = ny = nz = 0.0
    for i, (x, y, z) in enumerate(pts):
        x2, y2, z2 = pts[(i + 1) % len(pts)]
        nx += (y - y2) * (z + z2)
        ny += (z - z2) * (x + x2)
        nz += (x - x2) * (y + y2)
    m = math.sqrt(nx * nx + ny * ny + nz * nz) or 1e-9
    return (nx / m, ny / m, nz / m)


def build():
    """The sort: a stack of rings, plus the letter standing off the face."""
    plan = letter_plan()
    lu = [p[0] for c in plan for p in c]
    lv = [p[1] for c in plan for p in c]
    BW = (max(lu) - min(lu)) + 0.24          # body width -- the letter plus bearings
    BD = (max(lv) - min(lv)) + 0.30          # body depth -- the em

    verts, faces = [], []                    # faces: (indices, layer)

    def push(p):
        verts.append(p)
        return len(verts) - 1

    # profile of the shank: (height, all-round inset, front-face inset)
    profile = [
        (0.000, 0.028, 0.000),               # foot, chamfered
        (0.046, 0.000, 0.000),
        (0.430, 0.000, 0.000),
        (0.470, 0.000, 0.080),               # the nick -- which way up the sort goes
        (0.548, 0.000, 0.080),
        (0.588, 0.000, 0.000),
        (1.300, 0.000, 0.000),
        (HB,    0.020, 0.000),               # face, chamfered
    ]
    rings = [[push(p) for p in _ring(BW, BD, y, inset, nick)]
             for y, inset, nick in profile]

    faces.append((tuple(rings[0]), "body"))                    # foot, normal -y
    for lo, up in zip(rings, rings[1:]):
        for k in range(len(lo)):
            k1 = (k + 1) % len(lo)
            faces.append(((lo[k], up[k], up[k1], lo[k1]), "body"))
    faces.append((tuple(reversed(rings[-1])), "body"))         # the face, normal +y

    # the letter, standing off the face
    caps = []
    for c in plan:
        base = [push((u, HB, v)) for u, v in c]
        top = [push((u, HB + RELIEF, v)) for u, v in c]
        for k in range(len(c)):
            k1 = (k + 1) % len(c)
            faces.append(((base[k], top[k], top[k1], base[k1]), "letter"))
        caps.append(list(reversed(top)))
    faces.append((tuple(caps[0]), "ink"))
    holes = [tuple(h) for h in caps[1:]]

    edges = {}
    for fi, (idx, _) in enumerate(faces):
        for k in range(len(idx)):
            e = (idx[k], idx[(k + 1) % len(idx)])
            edges.setdefault((min(e), max(e)), []).append(fi)

    normals = [_newell([verts[i] for i in idx]) for idx, _ in faces]
    crease = set()
    for e, fs in edges.items():
        if len(fs) == 2:
            a, b = normals[fs[0]], normals[fs[1]]
            if sum(x * y for x, y in zip(a, b)) < math.cos(math.radians(22)):
                crease.add(e)

    return {"v": verts, "f": faces, "edges": edges, "crease": crease,
            "holes": holes, "w": BW, "d": BD}


# ---------------------------------------------------------------- drawing

def _cam(p, theta, tilt):
    x, y, z = p
    c, s = math.cos(theta), math.sin(theta)
    x, z = x * c + z * s, -x * s + z * c
    ct, st = math.cos(tilt), math.sin(tilt)
    y, z = y * ct - z * st, y * st + z * ct
    return (x, y, z)


def _level(n):
    lam = max(0.0, sum(a * b for a, b in zip(n, LIGHT)))
    lum = 0.15 + 0.85 * lam
    for i, edge in enumerate((0.86, 0.63, 0.41, 0.23)):
        if lum > edge:
            return i
    return 4


def _n(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def _poly(pts):
    return "M" + "L".join(f"{_n(x)} {_n(y)}" for x, y in pts) + "Z"


FILLS = [f'fill="{GROUND}"'] + [
    f'fill="url(#eng{i})" stroke="url(#eng{i})" stroke-width=".7"' for i in (1, 2, 3, 4)]


def defs():
    """Engraving screens, fixed to the plate. Opaque -- the painter needs them to cover."""
    out = []
    for i, (gap, w, cross) in enumerate(
            ((7.2, 0.70, False), (4.8, 0.80, False), (3.3, 0.95, False), (2.7, 1.05, True)),
            start=1):
        line = (f'<line x1="0" y1="0" x2="0" y2="{_n(gap)}" stroke="{INK}"'
                f' stroke-width="{w}"/>')
        if cross:
            line += (f'<line x1="0" y1="0" x2="{_n(gap)}" y2="0" stroke="{INK}"'
                     f' stroke-width="{w}"/>')
        out.append(f'<pattern id="eng{i}" width="{_n(gap)}" height="{_n(gap)}"'
                   f' patternUnits="userSpaceOnUse" patternTransform="rotate(-34)">'
                   f'<rect width="{_n(gap)}" height="{_n(gap)}" fill="{GROUND}"/>'
                   f'{line}</pattern>')
    out.append(f'<pattern id="engs" width="6.4" height="6.4" patternUnits="userSpaceOnUse"'
               f' patternTransform="rotate(-34)">'
               f'<line x1="0" y1="0" x2="0" y2="6.4" stroke="{INK}" stroke-width=".85"/>'
               f'</pattern>')
    return "".join(out)


def _frame(mesh, theta, cx, cy, s):
    V = [_cam(p, theta, TILT) for p in mesh["v"]]
    P = [(cx + x * s, cy - y * s) for x, y, _ in V]

    vis, shown = {}, {"body": [], "letter": [], "ink": []}
    for fi, (idx, layer) in enumerate(mesh["f"]):
        pts = [V[i] for i in idx]
        n = _newell(pts)
        vis[fi] = n[2] > 0.015
        if vis[fi]:
            depth = sum(p[2] for p in pts) / len(pts)
            shown[layer].append((depth, idx, _level(n)))

    body = []

    # cast shadow: the foot, thrown away from the lamp
    foot = mesh["f"][0][0]
    body.append(f'<path d="{_poly([(P[i][0] + 13, P[i][1] + 7) for i in foot])}"'
                f' fill="url(#engs)" opacity=".45"/>')

    def paint(layer):
        """Painter's algorithm, with runs of one tone merged into a single path."""
        out, run, lvl = [], [], None
        for _, idx, level in sorted(shown[layer]):
            if level != lvl and run:
                out.append(f'<path {FILLS[lvl]} d="{"".join(run)}"/>')
                run = []
            lvl = level
            run.append(_poly([P[i] for i in idx]))
        if run:
            out.append(f'<path {FILLS[lvl]} d="{"".join(run)}"/>')
        return "".join(out)

    def lines(layer):
        sil, cre = [], []
        for e, fs in mesh["edges"].items():
            owners = [f for f in fs if mesh["f"][f][1] == layer]
            if not owners:
                continue
            on = [f for f in owners if vis[f]]
            if not on:
                continue
            seen = sum(1 for f in fs if vis[f])
            seg = f"M{_n(P[e[0]][0])} {_n(P[e[0]][1])}L{_n(P[e[1]][0])} {_n(P[e[1]][1])}"
            if seen == 1 or len(fs) == 1:
                sil.append(seg)
            elif e in mesh["crease"]:
                cre.append(seg)
        out = ""
        if cre:
            out += (f'<path d="{"".join(cre)}" fill="none" stroke="{INK}"'
                    f' stroke-width=".75" opacity=".75" stroke-linecap="round"/>')
        if sil:
            out += (f'<path d="{"".join(sil)}" fill="none" stroke="{INK}"'
                    f' stroke-width="1.15" stroke-linecap="round"/>')
        return out

    body.append(paint("body"))
    body.append(lines("body"))
    body.append(paint("letter"))

    # the printing face: the one surface that would take ink, so the one oxblood mark
    if shown["ink"]:
        d = _poly([P[i] for i in mesh["f"][-1][0]])
        d += "".join(_poly([P[i] for i in h]) for h in mesh["holes"])
        body.append(f'<path d="{d}" fill-rule="evenodd" fill="{ACC}" stroke="{ACC}"'
                    f' stroke-width=".6" stroke-linejoin="round"/>')
    body.append(lines("letter"))
    return "".join(body)


def extent(mesh):
    """Screen bounds of the whole revolution, at unit scale. Lets a card centre it."""
    xs, ys = [], []
    for i in range(FRAMES):
        for p in mesh["v"]:
            x, y, _ = _cam(p, math.tau * i / FRAMES, TILT)
            xs.append(x)
            ys.append(y)
    return min(xs), max(xs), min(ys), max(ys)


def place(mesh, box):
    """(cx, cy, scale) that fits the revolution inside box = (x, y, w, h)."""
    bx, by, bw, bh = box
    x0, x1, y0, y1 = extent(mesh)
    s = min(bw / (x1 - x0), bh / (y1 - y0))
    return bx + bw / 2 - (x0 + x1) / 2 * s, by + bh / 2 + (y0 + y1) / 2 * s, s


def plate(cx, cy, s, mesh=None):
    """The turning sort, centred on (cx, cy). Returns SVG ready to drop in a card."""
    mesh = mesh or build()
    step = TURN / FRAMES
    out = []
    for i in range(FRAMES):
        delay = -((FRAMES - i) % FRAMES) * step
        out.append(f'<g class="fr" style="animation-delay:{delay:.3f}s">'
                   + _frame(mesh, math.tau * i / FRAMES, cx, cy, s) + '</g>')
    return "".join(out)


STYLE = (f"  .fr {{ opacity:0; animation:zoe {TURN}s linear infinite }}\n"
         f"  @keyframes zoe {{ 0%,{100/FRAMES - 0.05:.3f}% {{ opacity:1 }}"
         f" {100/FRAMES:.3f}%,100% {{ opacity:0 }} }}\n")
