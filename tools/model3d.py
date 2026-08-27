"""Loading and thinning a mesh.

The octopus arrives as 67k vertices and 90k triangles across 427 parts. Nothing
that heavy belongs in a repository that redraws itself nightly, and nothing that
heavy survives being turned into line work, so it is clustered down to a few
thousand faces and written back out as the copy the renderer actually reads.
"""
import numpy as np


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
