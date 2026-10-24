"""The octopus as it actually is: shaded, in its own materials.

The engraved version that came before this reads as a drawing, which is not what
the model looks like. This renders it properly instead -- z-buffer, smooth
normals, a metallic-roughness shading model, a soft cast shadow -- from the PBR
values lifted out of the GLB and kept in `data/materials.json`.

That forces the output to be raster. A shaded surface is a continuous gradient,
and there is no honest way to write forty frames of one as vector paths. So the
page gets an animated WebP, which is what a spinning model on a profile normally
is anyway.

Shading is deferred: the triangle loop writes only depth, normal and material id,
and the lighting runs once per frame over the whole buffer. Doing it per triangle
instead costs roughly three times as long for the same picture.

The lamp is fixed to the camera rather than to the world, so the highlight stays
where it is while the animal turns, and the shadow direction holds still while
its shape rotates. A world-fixed lamp makes the highlight sweep and strobe.
"""
import json
import math
from pathlib import Path

import numpy as np

import model3d

SS = 2                                  # render this many samples per output pixel
FRAMES = 40
TILT = math.radians(9)

LIGHT = np.array([0.44, 0.72, 0.58])    # key, upper right -- the shadow falls left
LIGHT = LIGHT / np.linalg.norm(LIGHT)
FILL = np.array([-0.58, 0.10, 0.34])    # weak bounce from the other side
FILL = FILL / np.linalg.norm(FILL)

KEY_C = np.array([1.18, 1.13, 1.04])    # slightly warm key
FILL_C = np.array([0.20, 0.22, 0.27])   # cool fill
SKY = np.array([0.37, 0.39, 0.43])      # hemispheric ambient, above
GRD = np.array([0.20, 0.19, 0.17])      # and below

PAPER = np.array([0xF5, 0xF1, 0xE8]) / 255.0
SHADOW_RGB = np.array([0.35, 0.33, 0.30])   # warm grey, not black
SHADOW_STRENGTH = 0.42
GROUND_Y = -0.012                       # the floor the shadow lands on


def _srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def _linear(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def camera(v, theta, tilt=TILT):
    c, s = math.cos(theta), math.sin(theta)
    x = v[:, 0] * c + v[:, 2] * s
    z = -v[:, 0] * s + v[:, 2] * c
    ct, st = math.cos(tilt), math.sin(tilt)
    return np.stack([x, v[:, 1] * ct - z * st, v[:, 1] * st + z * ct], axis=1)


def _unrotate(d, theta, tilt=TILT):
    """A camera-space direction expressed back in world space."""
    ct, st = math.cos(-tilt), math.sin(-tilt)
    y, z = d[1] * ct - d[2] * st, d[1] * st + d[2] * ct
    c, s = math.cos(-theta), math.sin(-theta)
    return np.array([d[0] * c + z * s, y, -d[0] * s + z * c])


class Shader:
    def __init__(self, obj, materials, box, canvas, frames=FRAMES, tilt=TILT, ss=SS):
        v, f, mats, names, parts = model3d.load_full(obj)
        self.v = model3d.normalise(v)
        self.f, self.m, self.names = f, mats, names
        self.n = model3d.vertex_normals(self.v, self.f)
        self.frames, self.tilt = frames, tilt

        table = json.loads(Path(materials).read_text())
        self.albedo = np.array([table[n]["base"] for n in names], dtype=np.float32)
        self.metal = np.array([table[n]["metallic"] for n in names], dtype=np.float32)
        self.rough = np.array([table[n]["roughness"] for n in names], dtype=np.float32)
        self.emit = np.array([table[n]["emissive"] for n in names], dtype=np.float32)

        self.ss = ss
        cw, ch = canvas
        self.W, self.H = cw * ss, ch * ss
        bx, by, bw, bh = box
        xs, ys = [], []
        for i in range(frames):
            P = camera(self.v, math.tau * i / frames, tilt)
            xs += [P[:, 0].min(), P[:, 0].max()]
            ys += [P[:, 1].min(), P[:, 1].max()]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        self.scale = min(bw / (x1 - x0), bh / (y1 - y0)) * ss
        self.cx = (bx + bw / 2 - (x0 + x1) / 2 * self.scale / ss) * ss
        self.cy = (by + bh / 2 + (y0 + y1) / 2 * self.scale / ss) * ss

        # A coarse copy carries the shadow. It is about to be blurred seven times,
        # so silhouette detail in it is wasted work.
        self.sv, self.sf, _ = model3d.cluster(
            self.v, self.f, np.zeros((len(self.f), 1)), grid=70)

        rng = np.random.RandomState(7)          # one grain field for every frame,
        self.grain = rng.normal(0, 1, (ch, cw, 1)) * 0.012   # or the paper crawls

    # ------------------------------------------------------------ raster

    def _gbuffer(self, P, N):
        sx = self.cx + P[:, 0] * self.scale
        sy = self.cy - P[:, 1] * self.scale
        f = self.f
        ax, ay, az = sx[f[:, 0]], sy[f[:, 0]], P[f[:, 0], 2]
        bx, by, bz = sx[f[:, 1]], sy[f[:, 1]], P[f[:, 1], 2]
        cx, cy, cz = sx[f[:, 2]], sy[f[:, 2]], P[f[:, 2], 2]
        ar = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

        x0 = np.clip(np.floor(np.minimum(np.minimum(ax, bx), cx)), 0, self.W - 1).astype(int)
        x1 = np.clip(np.ceil(np.maximum(np.maximum(ax, bx), cx)), 0, self.W - 1).astype(int)
        y0 = np.clip(np.floor(np.minimum(np.minimum(ay, by), cy)), 0, self.H - 1).astype(int)
        y1 = np.clip(np.ceil(np.maximum(np.maximum(ay, by), cy)), 0, self.H - 1).astype(int)

        depth = np.full((self.H, self.W), -1e30, dtype=np.float32)
        nrm = np.zeros((self.H, self.W, 3), dtype=np.float32)
        mid = np.full((self.H, self.W), -1, dtype=np.int16)

        na, nb, nc = N[f[:, 0]], N[f[:, 1]], N[f[:, 2]]
        # Back-face cull by the vertex normals, not by the winding: the winding is
        # consistent but inverted relative to the normals, and about 8% of triangles
        # disagree with it outright, so culling on the projected area sign punches
        # holes in the model. A triangle whose three normals all face away is behind.
        front = (na[:, 2] > -0.05) | (nb[:, 2] > -0.05) | (nc[:, 2] > -0.05)

        for i in range(len(f)):
            if not front[i] or ar[i] == 0 or x1[i] < x0[i] or y1[i] < y0[i]:
                continue
            gx = np.arange(x0[i], x1[i] + 1) + 0.5
            gy = (np.arange(y0[i], y1[i] + 1) + 0.5)[:, None]
            w0 = (bx[i] - ax[i]) * (gy - ay[i]) - (by[i] - ay[i]) * (gx - ax[i])
            w1 = (cx[i] - bx[i]) * (gy - by[i]) - (cy[i] - by[i]) * (gx - bx[i])
            w2 = (ax[i] - cx[i]) * (gy - cy[i]) - (ay[i] - cy[i]) * (gx - cx[i])
            inside = ((w0 >= 0) & (w1 >= 0) & (w2 >= 0)) | ((w0 <= 0) & (w1 <= 0) & (w2 <= 0))
            if not inside.any():
                continue
            u0, u1, u2 = w0 / ar[i], w1 / ar[i], w2 / ar[i]     # weights of c, a, b
            z = u0 * cz[i] + u1 * az[i] + u2 * bz[i]
            sl = (slice(y0[i], y1[i] + 1), slice(x0[i], x1[i] + 1))
            win = inside & (z > depth[sl])
            if not win.any():
                continue
            depth[sl] = np.where(win, z, depth[sl])
            mid[sl] = np.where(win, self.m[i], mid[sl])
            w = win[..., None]
            nrm[sl] = np.where(w, (u1[..., None] * na[i] + u2[..., None] * nb[i]
                                   + u0[..., None] * nc[i]), nrm[sl])
        return depth, nrm, mid

    def _shadow(self, theta):
        """Silhouette dropped onto the floor along the lamp, then blurred."""
        Lw = _unrotate(LIGHT, theta, self.tilt)
        if abs(Lw[1]) < 1e-3:
            return np.zeros((self.H, self.W))
        t = (self.sv[:, 1] - GROUND_Y) / Lw[1]
        flat = self.sv - t[:, None] * Lw[None, :]
        P = camera(flat, theta, self.tilt)

        sx = self.cx + P[:, 0] * self.scale
        sy = self.cy - P[:, 1] * self.scale
        f = self.sf
        ax, ay, bx, by, cx, cy = (sx[f[:, 0]], sy[f[:, 0]], sx[f[:, 1]],
                                  sy[f[:, 1]], sx[f[:, 2]], sy[f[:, 2]])
        ar = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

        h, w = max(1, self.H // 2), max(1, self.W // 2)               # half res: it is about to be blurred
        m = np.zeros((h, w), dtype=bool)
        x0 = np.clip(np.floor(np.minimum(np.minimum(ax, bx), cx) / 2), 0, w - 1).astype(int)
        x1 = np.clip(np.ceil(np.maximum(np.maximum(ax, bx), cx) / 2), 0, w - 1).astype(int)
        y0 = np.clip(np.floor(np.minimum(np.minimum(ay, by), cy) / 2), 0, h - 1).astype(int)
        y1 = np.clip(np.ceil(np.maximum(np.maximum(ay, by), cy) / 2), 0, h - 1).astype(int)
        for i in range(len(f)):
            if ar[i] == 0 or x1[i] < x0[i] or y1[i] < y0[i]:
                continue
            gx = (np.arange(x0[i], x1[i] + 1) + 0.5) * 2
            gy = ((np.arange(y0[i], y1[i] + 1) + 0.5) * 2)[:, None]
            w0 = (bx[i] - ax[i]) * (gy - ay[i]) - (by[i] - ay[i]) * (gx - ax[i])
            w1 = (cx[i] - bx[i]) * (gy - by[i]) - (cy[i] - by[i]) * (gx - bx[i])
            w2 = (ax[i] - cx[i]) * (gy - cy[i]) - (ay[i] - cy[i]) * (gx - cx[i])
            ins = ((w0 >= 0) & (w1 >= 0) & (w2 >= 0)) | ((w0 <= 0) & (w1 <= 0) & (w2 <= 0))
            sl = (slice(y0[i], y1[i] + 1), slice(x0[i], x1[i] + 1))
            m[sl] |= ins

        s = m.astype(np.float32)
        for _ in range(8):                            # cheap wide blur, softens with distance
            s = (s + np.roll(s, 1, 0) + np.roll(s, -1, 0)
                 + np.roll(s, 1, 1) + np.roll(s, -1, 1)) / 5
        s = np.repeat(np.repeat(s, 2, axis=0), 2, axis=1)[:self.H, :self.W]
        for _ in range(3):                            # nearest-neighbour upsampling leaves
            s = (s + np.roll(s, 1, 0) + np.roll(s, -1, 0)     # 2x2 blocks; smooth them out
                 + np.roll(s, 1, 1) + np.roll(s, -1, 1)) / 5
        return s

    # ------------------------------------------------------------ shading

    def frame(self, theta, background=True):
        P = camera(self.v, theta, self.tilt)
        Nv = camera(self.n, theta, self.tilt)
        depth, nrm, mid = self._gbuffer(P, Nv)
        mask = mid >= 0

        ln = np.linalg.norm(nrm, axis=2, keepdims=True)
        N = nrm / np.where(ln == 0, 1, ln)

        ix = np.clip(mid, 0, None)
        alb = self.albedo[ix]
        met = self.metal[ix][..., None]
        rgh = np.clip(self.rough[ix][..., None], 0.03, 1.0)
        emi = self.emit[ix]

        V = np.array([0.0, 0.0, 1.0])
        ndl = np.clip(N @ LIGHT, 0, 1)[..., None]
        ndf = np.clip(N @ FILL, 0, 1)[..., None]
        hv = LIGHT + V
        hv = hv / np.linalg.norm(hv)
        ndh = np.clip(N @ hv, 0, 1)[..., None]

        shine = np.clip(2.0 / np.maximum(rgh ** 4, 1e-4) - 2.0, 4, 2048)
        f0 = 0.04 * (1 - met) + alb * met
        kd = alb * (1 - met)

        hemi = 0.5 + 0.5 * N[..., 1:2]
        ambient = (GRD + (SKY - GRD) * hemi) * alb
        colour = (kd * ndl * KEY_C
                  + kd * ndf * FILL_C
                  + f0 * np.power(ndh, shine) * KEY_C * 0.9
                  + ambient
                  + emi)

        rgb = _srgb(colour)
        a_obj = mask.astype(float)[..., None]
        shadow = np.clip(self._shadow(theta), 0, 1)[..., None]

        if background:
            paper = _linear(PAPER)
            floor = _srgb(paper * (1.0 - SHADOW_STRENGTH * shadow))
            out = floor * (1 - a_obj) + rgb * a_obj
            alpha = np.ones_like(a_obj)
        else:
            # The shadow carries in the alpha instead of onto paper, so the page
            # itself is the floor and the image sits on either GitHub theme.
            a_sh = SHADOW_STRENGTH * shadow * (1 - a_obj)
            alpha = a_obj + a_sh
            out = np.where(alpha > 1e-6,
                           (rgb * a_obj + SHADOW_RGB * a_sh) / np.maximum(alpha, 1e-6),
                           0.0)

        k = self.ss
        out = out.reshape(self.H // k, k, self.W // k, k, 3).mean(axis=(1, 3))
        alpha = alpha.reshape(self.H // k, k, self.W // k, k, 1).mean(axis=(1, 3))
        if background:
            out = np.clip(out + self.grain, 0, 1)
        return np.clip(out, 0, 1), alpha[..., 0]


def turntable(sh, path, duration=100, quality=82, background=False):
    """One revolution as an animated WebP.

    WebP rather than GIF: the whole subject is smooth gradient and 256 colours
    dither it into mud. Browsers have supported animated WebP for years and
    GitHub serves it like any other image.

    With background, the animal stands on grained paper and the shadow is printed
    on it; without, the shadow rides in the alpha and the page is the floor.
    """
    from PIL import Image

    frames = []
    for i in range(sh.frames):
        rgb, a = sh.frame(math.tau * i / sh.frames, background=background)
        if background:
            frames.append(Image.fromarray((rgb * 255 + 0.5).astype(np.uint8), mode="RGB"))
            continue
        rgba = np.concatenate([rgb, a[..., None]], axis=2)
        frames.append(Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), mode="RGBA"))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=duration,
                   loop=0, quality=quality, method=4, minimize_size=True)
    return len(frames)
