"""Loading and thinning a mesh.

The octopus arrives as 67k vertices and 90k triangles across 427 parts. Nothing
that heavy belongs in a repository that redraws itself nightly, and nothing that
heavy survives being turned into line work, so it is clustered down to a few
thousand faces and written back out as the copy the renderer actually reads.
"""
import numpy as np


def load_full(path):
    """Vertices, triangles, a material index per triangle, the material names, and
    the part each triangle belongs to.

    The part matters. The model is 427 separate objects that touch but do not share
    geometry -- brass bands sitting on a bone arm. Weld them and both the decimation
    and the vertex normals smear one into the other.
    """
    verts, faces, mats, parts = [], [], [], []
    names, name_ix = [], {}
    cur, part = 0, -1
    with open(path) as fh:
        for line in fh:
            if line.startswith("v "):
                verts.append([float(v) for v in line.split()[1:4]])
            elif line.startswith("o "):
                part += 1
            elif line.startswith("usemtl "):
                n = line.split()[1].strip()
                if n not in name_ix:
                    name_ix[n] = len(names)
                    names.append(n)
                cur = name_ix[n]
            elif line.startswith("f "):
                idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
                for k in range(1, len(idx) - 1):
                    faces.append([idx[0], idx[k], idx[k + 1]])
                    mats.append(cur)
                    parts.append(max(part, 0))
    return (np.asarray(verts, dtype=np.float64), np.asarray(faces, dtype=np.int32),
            np.asarray(mats, dtype=np.int32), names, np.asarray(parts, dtype=np.int32))


def cluster(v, f, keep, grid=150, parts=None):
    """Vertex clustering, optionally kept inside each part.

    `keep` is any per-face array to carry through. Returns the new mesh plus the
    surviving rows of `keep`.
    """
    lo, hi = v.min(axis=0), v.max(axis=0)
    step = (hi - lo).max() / grid
    cell = np.floor((v - lo) / step).astype(np.int64)
    key = (cell[:, 0] * 100003 + cell[:, 1]) * 100003 + cell[:, 2]

    if parts is not None:
        # a vertex belongs to whichever part first claimed it; faces are what carry
        # the part id, so push it down to the vertices before hashing
        vpart = np.zeros(len(v), dtype=np.int64)
        vpart[f.reshape(-1)] = np.repeat(parts, 3)
        key = key * 1000003 + vpart

    order = np.argsort(key, kind="stable")
    uniq, first = np.unique(key[order], return_index=True)
    remap = np.empty(len(v), dtype=np.int32)
    remap[order] = np.repeat(np.arange(len(uniq), dtype=np.int32),
                             np.diff(np.append(first, len(order))))

    nv = np.zeros((len(uniq), 3))
    np.add.at(nv, remap, v)
    nv /= np.bincount(remap, minlength=len(uniq))[:, None]

    nf = remap[f]
    ok = ((nf[:, 0] != nf[:, 1]) & (nf[:, 1] != nf[:, 2]) & (nf[:, 0] != nf[:, 2]))
    nf, keep = nf[ok], keep[ok]

    _, uf = np.unique(np.sort(nf, axis=1), axis=0, return_index=True)
    uf.sort()
    return nv, nf[uf], keep[uf]


def vertex_normals(v, f):
    """Smooth normals, area-weighted. Parts do not share vertices, so this does not
    round off the joint between a brass band and the arm underneath it."""
    n = np.zeros_like(v)
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])   # length = 2*area
    for k in range(3):
        np.add.at(n, f[:, k], fn)
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1e-9
    return n / ln[:, None]


def write_full(path, v, f, mats, names):
    """The thinned copy the renderer reads, material groups intact."""
    out = [f"# nautilia-octopus, clustered to {len(f)} triangles\n"]
    out += [f"v {x:.5f} {y:.5f} {z:.5f}\n" for x, y, z in v]
    order = np.argsort(mats, kind="stable")
    last = None
    for i in order:
        if mats[i] != last:
            last = mats[i]
            out.append(f"usemtl {names[last]}\n")
        a, b, c = f[i] + 1
        out.append(f"f {a} {b} {c}\n")
    with open(path, "w") as fh:
        fh.writelines(out)


def load_obj(path, accent=("lens-glow",)):
    """Vertices, triangles, and a flag per triangle for the materials that print red."""
    verts, faces, flags = [], [], []
    hot = False
    with open(path) as fh:
        for line in fh:
            if line.startswith("v "):
                verts.append([float(v) for v in line.split()[1:4]])
            elif line.startswith("usemtl "):
                hot = line.split()[1].strip() in accent
            elif line.startswith("f "):
                # v, v/vt, v//vn and v/vt/vn all start with the vertex index
                idx = [int(p.split("/")[0]) - 1 for p in line.split()[1:]]
                for k in range(1, len(idx) - 1):        # fan-triangulate
                    faces.append([idx[0], idx[k], idx[k + 1]])
                    flags.append(hot)
    return (np.asarray(verts, dtype=np.float64),
            np.asarray(faces, dtype=np.int32),
            np.asarray(flags, dtype=bool))


def normalise(v):
    """Centre on the origin, stand on y=0, scale so the model is one unit tall."""
    lo, hi = v.min(axis=0), v.max(axis=0)
    v = v - [(lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2]
    return v / (hi[1] - lo[1])


def decimate(v, f, flags, grid=150):
    """Vertex clustering.

    Cheap, deterministic, and it keeps the silhouette -- which is all the engraver
    needs, since tone comes from the raster and not from the facets. Quadric
    collapse would hold the arms better but is not worth the dependency here.
    """
    lo, hi = v.min(axis=0), v.max(axis=0)
    step = (hi - lo).max() / grid
    cell = np.floor((v - lo) / step).astype(np.int64)
    key = (cell[:, 0] * 100003 + cell[:, 1]) * 100003 + cell[:, 2]

    order = np.argsort(key, kind="stable")
    uniq, first = np.unique(key[order], return_index=True)
    remap = np.empty(len(v), dtype=np.int32)
    remap[order] = np.repeat(np.arange(len(uniq), dtype=np.int32), np.diff(np.append(first, len(order))))

    nv = np.zeros((len(uniq), 3))
    np.add.at(nv, remap, v)
    counts = np.bincount(remap, minlength=len(uniq))
    nv /= counts[:, None]

    nf = remap[f]
    keep = ((nf[:, 0] != nf[:, 1]) & (nf[:, 1] != nf[:, 2]) & (nf[:, 0] != nf[:, 2]))
    nf, nflags = nf[keep], flags[keep]

    # one triangle per set of corners, whatever order they arrived in
    sig = np.sort(nf, axis=1)
    _, uf = np.unique(sig, axis=0, return_index=True)
    uf.sort()
    return nv, nf[uf], nflags[uf]


def write_obj(path, v, f, flags, name="nautilia-octopus"):
    """The thinned copy the renderer reads. Coordinates rounded -- this is a git repo."""
    out = [f"# {name}, clustered to {len(f)} triangles for the engraver\n"]
    out += [f"v {x:.5f} {y:.5f} {z:.5f}\n" for x, y, z in v]
    order = np.argsort(flags, kind="stable")            # plain faces first, then the lenses
    last = None
    for i in order:
        if bool(flags[i]) != last:
            last = bool(flags[i])
            out.append(f"usemtl {'lens-glow' if last else 'bone'}\n")
        a, b, c = f[i] + 1
        out.append(f"f {a} {b} {c}\n")
    with open(path, "w") as fh:
        fh.writelines(out)
