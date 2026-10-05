"""Geometry core: SVG path data <-> numpy polylines <-> shapely <-> skia-pathops.

Conventions
-----------
* A *d* is an SVG path-data string.  Everything that accepts "pathlike" takes a
  d-string, an (N,2) numpy array / list of points (open polyline), a list of such
  arrays, a list of ``(points, closed)`` tuples, or a shapely geometry.
* Coordinates are SVG px (y down). Output d-strings are rounded to 0.01 px and
  use relative commands for compactness (no drift: deltas are taken between
  already-rounded absolute points).
* ``Curve.normal`` points to the LEFT of the direction of travel as seen on
  screen (for a path heading +x the normal is (0,-1), i.e. up).
"""
from __future__ import annotations

import math
import re
from typing import Sequence

import numpy as np
import pathops
import shapely
from shapely.geometry import LinearRing, LineString, MultiLineString, Polygon

__all__ = [
    "parse_d", "cmds_to_d", "flatten", "as_polys", "poly_d", "polys_d", "join_d",
    "to_shape", "from_shape", "to_skia", "from_skia", "union", "difference", "intersection",
    "xor", "resolve", "clip", "offset", "outline", "simplify", "bbox", "area", "transform",
    "translate", "rotate", "scale", "mirror_x", "mirror_y", "mirror_line", "rotate180",
    "repeat_rotational", "bilateral", "reverse", "fillet", "Curve", "curve", "resample", "point_at",
    "tangent_at", "normal_at", "smooth_d", "spline", "circle_d", "ellipse_d", "rect_d",
    "arc_pts", "polygon_d", "star_d", "signed_area", "orient", "clip_out", "knockout",
    "fillet_junction", "interlace", "fit_curves", "round_corners",
]

TOL = 0.05  # default flattening tolerance (px)


# =============================================================================
# path data parsing / serialising
# =============================================================================
_CMD_RE = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]")
_NUM_RE = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_ARGC = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}


def parse_d(d: str) -> list[tuple]:
    """Parse SVG path data into absolute commands.

    Returns a list of tuples: ('M',x,y) ('L',x,y) ('C',x1,y1,x2,y2,x,y)
    ('Q',x1,y1,x,y) ('Z',). H/V/S/T are expanded, arcs become cubics.
    """
    out: list[tuple] = []
    i, n = 0, len(d)
    cx = cy = sx = sy = 0.0
    last_ctrl = None  # (type, x, y) of last control point for S/T
    cmd = None
    while i < n:
        ch = d[i]
        if ch in " \t\r\n,":
            i += 1
            continue
        if ch.isalpha():
            if ch not in _ARGC and ch.upper() not in _ARGC:
                raise ValueError(f"unknown path command {ch!r} near {d[i:i+20]!r}")
            cmd = ch
            i += 1
            if cmd in "Zz":
                out.append(("Z",))
                cx, cy = sx, sy
                last_ctrl = None
                continue
        elif cmd is None:
            raise ValueError("path data must start with a command")
        elif cmd in "Zz":
            # SVG: numbers may not follow closepath without a new command letter
            raise ValueError(f"coordinates after Z without a command near {d[i:i+20]!r}")
        up = cmd.upper()
        rel = cmd.islower()
        argc = _ARGC[up]
        args = []
        while len(args) < argc:
            while i < n and d[i] in " \t\r\n,":
                i += 1
            if i >= n:
                raise ValueError("truncated path data")
            if up == "A" and len(args) in (3, 4):
                if d[i] not in "01":
                    raise ValueError("bad arc flag")
                args.append(float(d[i]))
                i += 1
                continue
            m = _NUM_RE.match(d, i)
            if not m:
                raise ValueError(f"bad number near {d[i:i+20]!r}")
            args.append(float(m.group()))
            i = m.end()
        if up == "M":
            x, y = args
            if rel:
                x += cx; y += cy
            out.append(("M", x, y))
            cx, cy, sx, sy = x, y, x, y
            cmd = "l" if rel else "L"
            last_ctrl = None
        elif up in "LHV":
            if up == "L":
                x, y = args
                if rel:
                    x += cx; y += cy
            elif up == "H":
                x = args[0] + (cx if rel else 0); y = cy
            else:
                x = cx; y = args[0] + (cy if rel else 0)
            out.append(("L", x, y))
            cx, cy = x, y
            last_ctrl = None
        elif up == "C":
            x1, y1, x2, y2, x, y = args
            if rel:
                x1 += cx; y1 += cy; x2 += cx; y2 += cy; x += cx; y += cy
            out.append(("C", x1, y1, x2, y2, x, y))
            last_ctrl = ("C", x2, y2)
            cx, cy = x, y
        elif up == "S":
            x2, y2, x, y = args
            if rel:
                x2 += cx; y2 += cy; x += cx; y += cy
            if last_ctrl and last_ctrl[0] == "C":
                x1, y1 = 2 * cx - last_ctrl[1], 2 * cy - last_ctrl[2]
            else:
                x1, y1 = cx, cy
            out.append(("C", x1, y1, x2, y2, x, y))
            last_ctrl = ("C", x2, y2)
            cx, cy = x, y
        elif up == "Q":
            x1, y1, x, y = args
            if rel:
                x1 += cx; y1 += cy; x += cx; y += cy
            out.append(("Q", x1, y1, x, y))
            last_ctrl = ("Q", x1, y1)
            cx, cy = x, y
        elif up == "T":
            x, y = args
            if rel:
                x += cx; y += cy
            if last_ctrl and last_ctrl[0] == "Q":
                x1, y1 = 2 * cx - last_ctrl[1], 2 * cy - last_ctrl[2]
            else:
                x1, y1 = cx, cy
            out.append(("Q", x1, y1, x, y))
            last_ctrl = ("Q", x1, y1)
            cx, cy = x, y
        elif up == "A":
            rx, ry, rot, large, sweep, x, y = args
            if rel:
                x += cx; y += cy
            out.extend(_arc_to_cubics(cx, cy, rx, ry, rot, large, sweep, x, y))
            cx, cy = x, y
            last_ctrl = None
    return out


def _arc_to_cubics(x1, y1, rx, ry, phi_deg, fa, fs, x2, y2):
    if (x1 == x2 and y1 == y2):
        return []
    rx, ry = abs(rx), abs(ry)
    if rx == 0 or ry == 0:
        return [("L", x2, y2)]
    phi = math.radians(phi_deg % 360)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p = cp * dx + sp * dy
    y1p = -sp * dx + cp * dy
    lam = (x1p / rx) ** 2 + (y1p / ry) ** 2
    if lam > 1:
        s = math.sqrt(lam)
        rx *= s; ry *= s
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if fa == fs:
        co = -co
    cxp = co * rx * y1p / ry
    cyp = -co * ry * x1p / rx
    ccx = cp * cxp - sp * cyp + (x1 + x2) / 2
    ccy = sp * cxp + cp * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    nseg = max(1, int(math.ceil(abs(dt) / (math.pi / 2) - 1e-9)))
    d = dt / nseg
    k = 4 / 3 * math.tan(d / 4)
    out = []
    t = t1
    for _ in range(nseg):
        c1, s1 = math.cos(t), math.sin(t)
        c2, s2 = math.cos(t + d), math.sin(t + d)
        p = [(c1 - k * s1, s1 + k * c1), (c2 + k * s2, s2 - k * c2), (c2, s2)]
        q = []
        for ux, uy in p:
            ux *= rx; uy *= ry
            q += [cp * ux - sp * uy + ccx, sp * ux + cp * uy + ccy]
        out.append(("C", *q))
        t += d
    # snap final point exactly
    last = list(out[-1]); last[5], last[6] = x2, y2
    out[-1] = tuple(last)
    return out


def _cents(v):
    if not math.isfinite(v):
        raise ValueError(f"non-finite coordinate {v!r} in path data")
    return int(round(v * 100))


def _fc(c: int) -> str:
    """format integer hundredths as compact decimal string."""
    if c == 0:
        return "0"
    s = "-" if c < 0 else ""
    c = abs(c)
    ip, fp = divmod(c, 100)
    if fp == 0:
        return f"{s}{ip}"
    fs = f"{fp:02d}".rstrip("0")
    return f"{s}{ip}.{fs}" if ip else f"{s}.{fs}"


def cmds_to_d(cmds: Sequence[tuple]) -> str:
    """Serialise absolute commands (as returned by parse_d) to compact relative d."""
    out = []
    px = py = 0  # current point in cents
    sx = sy = 0
    prev = None
    for c in cmds:
        t = c[0]
        if t == "Z":
            out.append("z")
            px, py = sx, sy
            prev = "z"
            continue
        vals = [_cents(v) for v in c[1:]]
        if t == "M":
            x, y = vals
            out.append(f"M{_fc(x)} {_fc(y)}")
            px, py, sx, sy = x, y, x, y
            prev = "M"
            continue
        rel = []
        for j in range(0, len(vals), 2):
            rel += [vals[j] - px, vals[j + 1] - py]
        if t == "L":
            if rel == [0, 0]:
                continue
            key = "l"
        elif t == "C":
            key = "c"
        else:
            key = "q"
        body = " ".join(_fc(v) for v in rel)
        if prev == key:
            out.append(" " + body)
        else:
            out.append(key + body)
        prev = key
        px, py = vals[-2], vals[-1]
    return "".join(out)


# =============================================================================
# flattening
# =============================================================================
def _flat_cubic(p0, p1, p2, p3, tol):
    dd = max(math.hypot(p0[0] - 2 * p1[0] + p2[0], p0[1] - 2 * p1[1] + p2[1]),
             math.hypot(p1[0] - 2 * p2[0] + p3[0], p1[1] - 2 * p2[1] + p3[1]))
    n = max(1, min(2000, int(math.ceil(math.sqrt(0.75 * dd / tol))))) if dd > 0 else 1
    t = np.linspace(0, 1, n + 1)[1:, None]
    mt = 1 - t
    P = np.array([p0, p1, p2, p3], float)
    return mt ** 3 * P[0] + 3 * mt * mt * t * P[1] + 3 * mt * t * t * P[2] + t ** 3 * P[3]


def _flat_quad(p0, p1, p2, tol):
    dd = math.hypot(p0[0] - 2 * p1[0] + p2[0], p0[1] - 2 * p1[1] + p2[1])
    n = max(1, min(2000, int(math.ceil(math.sqrt(0.25 * dd / tol))))) if dd > 0 else 1
    t = np.linspace(0, 1, n + 1)[1:, None]
    mt = 1 - t
    P = np.array([p0, p1, p2], float)
    return mt * mt * P[0] + 2 * mt * t * P[1] + t * t * P[2]


def flatten(d, tol: float = TOL) -> list[tuple[np.ndarray, bool]]:
    """Flatten path data (string or command list) to [(points (N,2), closed), ...]."""
    cmds = parse_d(d) if isinstance(d, str) else d
    subs: list[tuple[np.ndarray, bool]] = []
    cur: list = []
    start = None
    pos = (0.0, 0.0)

    def flush(closed):
        nonlocal cur
        if cur:
            pts = np.vstack(cur)
            if closed and len(pts) > 1 and np.allclose(pts[0], pts[-1]):
                pts = pts[:-1]
            if len(pts) >= 2 or (closed and len(pts) >= 1):
                subs.append((pts, closed))
        cur = []

    for c in cmds:
        t = c[0]
        if t == "M":
            flush(False)
            pos = (c[1], c[2])
            start = pos
            cur = [np.array([pos])]
        elif t == "Z":
            flush(True)
            pos = start if start is not None else pos
        else:
            if not cur:
                cur = [np.array([pos])]
            if t == "L":
                pos = (c[1], c[2])
                cur.append(np.array([pos]))
            elif t == "C":
                cur.append(_flat_cubic(pos, c[1:3], c[3:5], c[5:7], tol))
                pos = (c[5], c[6])
            elif t == "Q":
                cur.append(_flat_quad(pos, c[1:3], c[3:5], tol))
                pos = (c[3], c[4])
    flush(False)
    return subs


def as_polys(x, tol: float = TOL) -> list[tuple[np.ndarray, bool]]:
    """Normalise any pathlike into [(points, closed), ...]."""
    if x is None:
        return []
    if isinstance(x, str):
        return flatten(x, tol) if x.strip() else []
    if isinstance(x, shapely.Geometry):
        return _shape_polys(x)
    if isinstance(x, Curve):
        return [(x.pts, x.closed)]
    if isinstance(x, np.ndarray) and x.ndim == 2:
        return [(x.astype(float), False)]
    if isinstance(x, (list, tuple)):
        if len(x) == 0:
            return []
        if len(x) == 2 and isinstance(x[1], (bool, np.bool_)):
            return [(np.asarray(x[0], float), bool(x[1]))]
        first = x[0]
        if isinstance(first, (int, float, np.floating, np.integer)):
            raise TypeError("a flat number list is not pathlike")
        if (isinstance(first, (list, tuple, np.ndarray)) and len(first) == 2 and
                isinstance(first[0], (int, float, np.floating, np.integer))):
            return [(np.asarray(x, float), False)]
        out = []
        for item in x:
            out += as_polys(item, tol)
        return out
    raise TypeError(f"not pathlike: {type(x)}")


def _shape_polys(gm) -> list:
    out = []
    if gm.is_empty:
        return out
    if isinstance(gm, Polygon):
        out.append((np.asarray(gm.exterior.coords)[:-1], True))
        for r in gm.interiors:
            out.append((np.asarray(r.coords)[:-1], True))
    elif isinstance(gm, LinearRing):
        out.append((np.asarray(gm.coords)[:-1], True))
    elif isinstance(gm, LineString):
        out.append((np.asarray(gm.coords), False))
    elif hasattr(gm, "geoms"):
        for sub in gm.geoms:
            out += _shape_polys(sub)
    return out


def signed_area(pts) -> float:
    """Shoelace area of a ring in SVG (y-down) coordinates: > 0 means the ring
    runs CLOCKWISE on screen (the inkkit convention for filled outlines)."""
    r = np.asarray(pts, float)
    if len(r) < 3:
        return 0.0
    return 0.5 * float(np.sum(r[:, 0] * np.roll(r[:, 1], -1) - np.roll(r[:, 0], -1) * r[:, 1]))


def poly_d(pts, closed: bool = False, orient: str | None = None) -> str:
    """Encode one polyline as compact relative path data (0.01 px grid).

    ``orient`` ('cw' | 'ccw', closed rings only) forces the screen winding
    direction — FILL pieces should be 'cw' (holes 'ccw') so that separately
    generated pieces can be concatenated under the nonzero rule."""
    A = np.asarray(pts, float)
    if len(A) == 0:
        return ""
    if A.ndim != 2 or A.shape[1] != 2:
        raise ValueError(f"poly_d expects (N,2) points, got shape {A.shape}")
    if not np.isfinite(A).all():
        raise ValueError("poly_d: non-finite (NaN/inf) coordinates")
    if orient is not None and closed and len(A) >= 3:
        if orient not in ("cw", "ccw"):
            raise ValueError(f"orient must be 'cw' or 'ccw', not {orient!r}")
        a = signed_area(A)
        if (a < 0 and orient == "cw") or (a > 0 and orient == "ccw"):
            A = A[::-1]
    P = np.rint(A * 100).astype(np.int64)
    D = np.diff(P, axis=0)
    keep = np.any(D != 0, axis=1)
    D = D[keep]
    parts = [f"M{_fc(int(P[0, 0]))} {_fc(int(P[0, 1]))}"]
    if len(D):
        parts.append("l" + " ".join(f"{_fc(int(a))} {_fc(int(b))}" for a, b in D))
    if closed:
        parts.append("z")
    return "".join(parts)


def polys_d(polys) -> str:
    """Encode [(pts, closed), ...] (or any pathlike) as one d string."""
    if isinstance(polys, str):
        return polys
    return "".join(poly_d(p, c) for p, c in as_polys(polys))


def join_d(*ds) -> str:
    """Concatenate d-strings / pathlikes into one d."""
    out = []
    for d in ds:
        if d is None:
            continue
        if isinstance(d, str):
            out.append(d)
        elif isinstance(d, (list, tuple)) and d and all(isinstance(s, str) for s in d):
            out.append("".join(d))
        else:
            out.append(polys_d(d))
    return "".join(out)


# =============================================================================
# skia-pathops bridge (exact bézier booleans)
# =============================================================================
_FILL = {"nonzero": pathops.FillType.WINDING, "evenodd": pathops.FillType.EVEN_ODD}


def to_skia(x, fill_rule: str = "nonzero", close: bool = True) -> pathops.Path:
    """Build a pathops.Path from a d-string (keeps curves) or any pathlike."""
    p = pathops.Path(fillType=_FILL[fill_rule])
    if isinstance(x, pathops.Path):
        return x
    if isinstance(x, str):
        open_ = False
        for c in parse_d(x):
            t = c[0]
            if t == "M":
                if open_ and close:
                    p.close()
                p.moveTo(c[1], c[2]); open_ = True
            elif t == "L":
                p.lineTo(c[1], c[2])
            elif t == "C":
                p.cubicTo(*c[1:])
            elif t == "Q":
                p.quadTo(*c[1:])
            elif t == "Z":
                p.close(); open_ = False
        if open_ and close:
            p.close()
        return p
    for pts, closed in as_polys(x):
        if len(pts) < 2:
            continue
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        if closed or close:
            p.close()
    return p


def from_skia(p: pathops.Path) -> str:
    """pathops.Path -> compact d (raw skia verbs; conics become quads)."""
    V = pathops.PathVerb
    cmds = []
    for verb, pts in p:
        if verb == V.MOVE:
            cmds.append(("M", *pts[0]))
        elif verb == V.LINE:
            cmds.append(("L", *pts[0]))
        elif verb == V.QUAD:
            cmds.append(("Q", *pts[0], *pts[1]))
        elif verb == V.CUBIC:
            cmds.append(("C", *pts[0], *pts[1], *pts[2]))
        elif verb == V.CLOSE:
            cmds.append(("Z",))
        else:  # conic: convert and recurse
            q = pathops.Path(fillType=p.fillType)
            q.addPath(p)
            q.convertConicsToQuads()
            return from_skia(q)
    return cmds_to_d(cmds)


_SHAPELY_OP = {pathops.PathOp.UNION: "union", pathops.PathOp.DIFFERENCE: "difference",
               pathops.PathOp.INTERSECTION: "intersection", pathops.PathOp.XOR: "symmetric_difference"}


def _jiggle(p: pathops.Path, eps: float) -> pathops.Path:
    q = pathops.Path(fillType=p.fillType)
    q.addPath(p)
    q.transform(1.0, 0.0, 0.0, 1.0, eps, eps * 0.7)
    return q


def _sk_simplified(p: pathops.Path) -> pathops.Path:
    q = pathops.Path(fillType=p.fillType)
    q.addPath(p)
    try:
        q.simplify(fix_winding=True)
    except pathops.PathOpsError:
        pass
    return q


def _sk_op(a: pathops.Path, b: pathops.Path, op) -> pathops.Path:
    """pathops.op with retries (simplify inputs, then sub-micro jiggle), and a
    shapely fallback — skia occasionally rejects exactly coincident edges."""
    try:
        return pathops.op(a, b, op, fix_winding=True)
    except pathops.PathOpsError:
        pass
    a2, b2 = _sk_simplified(a), _sk_simplified(b)
    for eps in (0.0, 1e-4, 1.7e-3):
        try:
            return pathops.op(a2, _jiggle(b2, eps) if eps else b2, op, fix_winding=True)
        except pathops.PathOpsError:
            continue
    # last resort: shapely, assembling rings by the path's own fill rule
    asm = _rings_to_shape if a.fillType == pathops.FillType.EVEN_ODD else _rings_to_shape_oriented
    sa = asm([p for p, c in flatten(from_skia(a2), 0.02) if len(p) >= 3])
    sb = asm([p for p, c in flatten(from_skia(b2), 0.02) if len(p) >= 3])
    res = getattr(sa, _SHAPELY_OP[op])(sb)
    return to_skia(_shape_polys(res))


def _op(a, b, op, fill_rule="nonzero"):
    if (_fast_ok(a) or _fast_ok(b)) and not any(isinstance(v, str) and _CURVE_RE.search(v) and len(v) > FAST_SEGMENTS * 8
                                                 for v in (a, b)):
        sa, sb = to_shape(a, fill_rule), to_shape(b, fill_rule)
        return from_shape(getattr(sa, _SHAPELY_OP[op])(sb))
    pa, pb = to_skia(a, fill_rule), to_skia(b, fill_rule)
    return from_skia(_sk_op(pa, pb, op))


def _blank(x) -> bool:
    """True for None / '' / empty containers / empty shapely geometry."""
    if x is None:
        return True
    if isinstance(x, str):
        return not x.strip()
    if isinstance(x, shapely.Geometry):
        return x.is_empty
    if isinstance(x, np.ndarray):
        return x.size == 0
    if isinstance(x, (list, tuple)):
        return len(x) == 0
    return False


def _sk_union_all(paths: list) -> pathops.Path:
    """Union of skia paths: each is resolved on its own, then only paths whose
    bounds overlap are merged (balanced pairwise tree of exact ``pathops.op``
    calls). Disjoint pieces are simply concatenated, which keeps unions of
    many small ornaments fast."""
    paths = [_sk_simplified(p) for p in paths]
    paths = [p for p in paths if len(p)]
    if not paths:
        return pathops.Path()
    if len(paths) == 1:
        return paths[0]
    boxes = [shapely.box(*p.bounds) for p in paths]
    tree = shapely.STRtree(boxes)
    parent = list(range(len(paths)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    a_idx, b_idx = tree.query(boxes, predicate="intersects")
    for i, j in zip(a_idx, b_idx):
        ri, rj = find(int(i)), find(int(j))
        if ri != rj:
            parent[ri] = rj
    groups: dict[int, list] = {}
    for i in range(len(paths)):
        groups.setdefault(find(i), []).append(paths[i])
    out = pathops.Path(fillType=pathops.FillType.WINDING)
    for grp in groups.values():
        if len(grp) > 24:
            # large overlapping clusters: GEOS cascaded union of the (already
            # resolved) pieces is much faster than a tree of skia ops
            shapes = [_rings_to_shape([q for q, c in flatten(from_skia(g), 0.02) if len(q) >= 3]) for g in grp]
            u = shapely.union_all([sh for sh in shapes if not sh.is_empty])
            out.addPath(to_skia(from_shape(u)))
            continue
        while len(grp) > 1:
            nxt = []
            for k in range(0, len(grp) - 1, 2):
                nxt.append(_sk_op(grp[k], grp[k + 1], pathops.PathOp.UNION))
            if len(grp) % 2:
                nxt.append(grp[-1])
            grp = nxt
        out.addPath(grp[0])
    return out


def union(*items, fill_rule: str = "nonzero") -> str:
    """Exact union of any number of pathlikes (curves preserved).

    The result is non-overlapping and consistently wound (outer rings
    clockwise on screen, holes counter-clockwise)."""
    items = [i for i in items if not _blank(i)]
    if not items:
        return ""
    return from_skia(_sk_union_all([to_skia(it, fill_rule) for it in items]))


def difference(a, *bs, fill_rule: str = "nonzero") -> str:
    """a minus every b."""
    if _blank(a):
        return ""
    acc = to_skia(a, fill_rule)
    for x in bs:
        if not _blank(x):
            acc = _sk_op(acc, to_skia(x, fill_rule), pathops.PathOp.DIFFERENCE)
    return from_skia(acc)


def intersection(a, b, fill_rule: str = "nonzero") -> str:
    if _blank(a) or _blank(b):
        return ""
    return _op(a, b, pathops.PathOp.INTERSECTION, fill_rule)


def xor(a, b, fill_rule: str = "nonzero") -> str:
    if _blank(a):
        return union(b, fill_rule=fill_rule)
    if _blank(b):
        return union(a, fill_rule=fill_rule)
    return _op(a, b, pathops.PathOp.XOR, fill_rule)


def resolve(d, fill_rule: str = "nonzero") -> str:
    """Remove self-overlaps: returns an equivalent non-overlapping path."""
    return from_skia(_sk_simplified(to_skia(d, fill_rule)))


# =============================================================================
# shapely bridge
# =============================================================================
def _inner_point(pg: Polygon):
    """A point strictly inside a (possibly invalid) ring polygon."""
    try:
        q = pg.representative_point() if pg.is_valid else shapely.make_valid(pg).representative_point()
    except shapely.errors.GEOSException:  # pragma: no cover - defensive
        q = pg.centroid
    return q.x, q.y


def _split_pinched(r: np.ndarray, depth: int = 0) -> list:
    """Split a ring that touches itself at a vertex (a 'pinch', common in
    resolved boolean output) into simple loops."""
    if len(r) < 6 or depth > 50:
        return [r]
    key = np.round(r, 6)
    seen = {}
    for i, k in enumerate(map(tuple, key)):
        if k in seen:
            j0 = seen[k]
            a = r[j0:i]
            b = np.vstack([r[i:], r[:j0]])
            return _split_pinched(a, depth + 1) + _split_pinched(b, depth + 1)
        seen[k] = i
    return [r]


def _ring_items(rings):
    items = []
    for r0 in rings:
        for r in _split_pinched(np.asarray(r0, float)):
            items.extend(_ring_item(r))
    items.sort(key=lambda t: -t[0])
    return items


def _ring_item(r):
    if len(r) < 3:
        return []
    a = signed_area(r)
    if abs(a) < 1e-9:
        return []
    return [(abs(a), float(np.sign(a)), Polygon(r), r)]


def _containers(items):
    """For each ring: the list of strictly larger rings containing a point
    strictly inside it (tested with a representative interior point, never a
    vertex, so rings that touch at a vertex are classified correctly)."""
    geoms = [it[2] for it in items]
    tree = shapely.STRtree(geoms)
    out = []
    for i, it in enumerate(items):
        x, y = _inner_point(it[2])
        cont = [int(j) for j in tree.query(shapely.points(x, y))
                if j != i and items[j][0] > it[0] and shapely.contains_xy(geoms[j], x, y)]
        cont.sort(key=lambda j: items[j][0])  # innermost first
        out.append(cont)
    return out


def _assemble(shells_holes, items):
    polys = []
    for i, holes in shells_holes.items():
        pg = Polygon(items[i][3], [items[h][3] for h in holes])
        if not pg.is_valid:
            # holes touching the shell at several vertices split the interior;
            # set difference handles that where make_valid mis-assigns faces
            sh = items[i][2] if items[i][2].is_valid else shapely.make_valid(items[i][2])
            hs = [items[h][2] if items[h][2].is_valid else shapely.make_valid(items[h][2]) for h in holes]
            pg = sh.difference(shapely.union_all(hs)) if hs else sh
        polys.append(pg)
    if not polys:
        return Polygon()
    return shapely.union_all(polys) if len(polys) > 1 else polys[0]


def _rings_to_shape(rings: list[np.ndarray]):
    """Even-odd assembly of rings by containment parity."""
    items = _ring_items(rings)
    if not items:
        return Polygon()
    cont = _containers(items)
    shells = {i: [] for i in range(len(items)) if len(cont[i]) % 2 == 0}
    for i in range(len(items)):
        if len(cont[i]) % 2 == 1 and cont[i][0] in shells:
            shells[cont[i][0]].append(i)
    return _assemble(shells, items)


def _rings_to_shape_oriented(rings: list[np.ndarray]):
    """Nonzero-style assembly: a ring is a hole of its innermost container
    when their orientations differ; overlapping same-direction shells are
    unioned (so concatenated, overlapping outlines stay solid). Exact for the
    well-formed (resolved) rings that skia-pathops produces."""
    items = _ring_items(rings)
    if not items:
        return Polygon()
    cont = _containers(items)
    shells: dict[int, list] = {}
    holes = []
    for i in range(len(items)):
        outside = sum(items[j][1] for j in cont[i])
        inside = outside + items[i][1]
        if inside != 0:
            shells[i] = []
        elif outside != 0:
            holes.append(i)
    for i in holes:
        host = next((j for j in cont[i] if j in shells), None)
        if host is not None:
            shells[host].append(i)
    return _assemble(shells, items)


_CURVE_RE = re.compile(r"[CcQqSsTtAa]")
FAST_SEGMENTS = 2500  # polygonal paths above this size use the shapely route


def _signed(r):
    return signed_area(r)


def _fast_ok(x) -> bool:
    return isinstance(x, str) and len(x) > FAST_SEGMENTS * 8 and not _CURVE_RE.search(x)


def to_shape(x, fill_rule: str = "nonzero", tol: float = TOL):
    """Pathlike -> shapely (Multi)Polygon, respecting the fill rule.

    Overlaps are resolved exactly by skia-pathops before flattening (its
    output is consistently wound, so rings are assembled by orientation);
    very large curve-free paths take a shapely route instead
    (orientation-aware ring assembly for nonzero, containment parity for
    evenodd) because pathops slows down badly on 10^5-segment polylines."""
    if isinstance(x, shapely.Geometry):
        return x
    if fill_rule not in _FILL:
        raise ValueError(f"fill_rule must be 'nonzero' or 'evenodd', not {fill_rule!r}")
    if _blank(x):
        return Polygon()
    if _fast_ok(x):
        rings = [p for p, c in flatten(x, tol) if len(p) >= 3]
        return _rings_to_shape(rings) if fill_rule == "evenodd" else _rings_to_shape_oriented(rings)
    p = to_skia(x, fill_rule)
    try:
        p.simplify(fix_winding=True)
    except pathops.PathOpsError:
        for eps in (1e-4, 1.7e-3):          # skia occasionally rejects near-degenerate input
            try:
                p = _jiggle(to_skia(x, fill_rule), eps)
                p.simplify(fix_winding=True)
                break
            except pathops.PathOpsError:
                continue
        else:
            rings = [pts for pts, closed in flatten(x if isinstance(x, str) else polys_d(x), tol)
                     if len(pts) >= 3]
            return _rings_to_shape(rings) if fill_rule == "evenodd" else _rings_to_shape_oriented(rings)
    rings = [pts for pts, closed in flatten(from_skia(p), tol) if len(pts) >= 3]
    return _rings_to_shape(rings)  # resolved rings never cross: nesting parity is exact


def from_shape(gm) -> str:
    """shapely geometry -> d (polygons closed, lines open). Polygons are
    oriented to the inkkit FILL convention: exteriors clockwise on screen,
    holes counter-clockwise."""
    if gm is None or gm.is_empty:
        return ""
    if isinstance(gm, (Polygon, shapely.MultiPolygon, shapely.GeometryCollection)):
        gm = shapely.orient_polygons(gm, exterior_cw=False)
    return polys_d(_shape_polys(gm))


def orient(x, direction: str = "cw") -> str:
    """Force every CLOSED subpath of ``x`` to wind ``direction`` ('cw' | 'ccw'
    on screen); curves are kept. Use on hole-free FILL pieces (dots, petals,
    solid shapes) so they compose by concatenation; use :func:`union` /
    :func:`resolve` for shapes with holes."""
    if direction not in ("cw", "ccw"):
        raise ValueError(f"direction must be 'cw' or 'ccw', not {direction!r}")
    d = x if isinstance(x, str) else polys_d(x)
    if not d.strip():
        return ""
    out = []
    for sub in _split_subpaths(parse_d(d)):
        closed = sub[-1][0] == "Z"
        if closed:
            pts = flatten(sub, 0.25)
            a = signed_area(pts[0][0]) if pts else 0.0
            if (a < 0 and direction == "cw") or (a > 0 and direction == "ccw"):
                out.append(reverse(cmds_to_d(sub)))
                continue
        out.append(cmds_to_d(sub))
    return "".join(out)


def _split_subpaths(cmds):
    subs, cur = [], []
    for c in cmds:
        if c[0] == "M" and cur:
            subs.append(cur)
            cur = []
        cur.append(c)
    if cur:
        subs.append(cur)
    return subs


def clip(x, shape, fill_rule: str = "nonzero", tol: float = TOL) -> str:
    """Clip OPEN polylines (stroke art) to a region; returns open-path d.
    For closed/filled art use :func:`intersection`."""
    region = to_shape(shape, fill_rule, tol) if not isinstance(shape, shapely.Geometry) else shape
    lines = [LineString(p if not c else np.vstack([p, p[:1]])) for p, c in as_polys(x, tol) if len(p) >= 2]
    if not lines or region.is_empty:
        return ""
    res = shapely.intersection(MultiLineString(lines), region)
    return from_shape(res)


def clip_out(x, shape, fill_rule: str = "nonzero", tol: float = TOL) -> str:
    """The parts of OPEN polylines (STROKE art) lying OUTSIDE a region — the
    complement of :func:`clip`. Returns open-path d."""
    region = to_shape(shape, fill_rule, tol) if not isinstance(shape, shapely.Geometry) else shape
    lines = [LineString(p if not c else np.vstack([p, p[:1]])) for p, c in as_polys(x, tol) if len(p) >= 2]
    if not lines:
        return ""
    if region.is_empty:
        return polys_d([(np.asarray(l.coords), False) for l in lines])
    res = shapely.difference(MultiLineString(lines), region)
    try:
        res = shapely.line_merge(res)
    except shapely.errors.GEOSException:  # pragma: no cover
        pass
    return from_shape(res)


def _qsegs(r):
    return int(max(4, min(32, 3 * math.sqrt(max(r, 0.1)) + 3)))


_JOIN = {"round": "round", "miter": "mitre", "mitre": "mitre", "bevel": "bevel"}
_CAP = {"round": "round", "flat": "flat", "butt": "flat", "square": "square"}


def offset(x, dist: float, join: str = "round", miter_limit: float = 4.0,
           fill_rule: str = "nonzero", tol: float = TOL) -> str:
    """Grow (dist>0) or shrink (dist<0) a filled shape. Returns d."""
    if join not in _JOIN:
        raise ValueError(f"join must be one of {sorted(_JOIN)}, not {join!r}")
    s = to_shape(x, fill_rule, tol)
    if s.is_empty:
        return ""
    if dist == 0:
        return from_shape(s)
    r = s.buffer(dist, quad_segs=_qsegs(abs(dist)), join_style=_JOIN[join], mitre_limit=miter_limit)
    return from_shape(r)


def outline(x, width: float, cap: str = "round", join: str = "round", miter_limit: float = 4.0,
            tol: float = TOL, simplify: float = 0.02, as_shape: bool = False):
    """Monoline stroke -> filled outline (union of all subpaths). Closed subpaths
    are stroked as rings.  Use this to turn STROKE-type output into FILL art.
    ``simplify`` px DP tolerance on the result; ``as_shape`` returns shapely.
    Heavy inputs (> 400 lines or > 20k vertices) are unioned in overlapping
    120 px tiles (fast; the result is concat-safe clockwise pieces rather than
    one outline)."""
    geoms = []
    for pts, closed in as_polys(x, tol):
        if len(pts) < 2:
            continue
        if closed and len(pts) >= 3:
            geoms.append(LinearRing(pts))
        else:
            geoms.append(LineString(pts))
    if not geoms:
        return Polygon() if as_shape else ""
    if not width > 0:
        raise ValueError(f"outline width must be > 0, got {width!r}")
    if cap not in _CAP or join not in _JOIN:
        raise ValueError(f"cap must be one of {sorted(_CAP)}, join one of {sorted(_JOIN)}")
    r = width / 2
    kw = dict(quad_segs=_qsegs(r), cap_style=_CAP[cap], join_style=_JOIN[join], mitre_limit=miter_limit)
    buf = shapely.buffer(np.array(geoms, dtype=object), r, **kw)
    heavy = len(geoms) > 400 or int(shapely.get_num_coordinates(np.array(geoms, dtype=object)).sum()) > 20000
    if heavy and not as_shape:
        # many crossing lines (lattices, big hatch fields): union tile by tile.
        # Tiles overlap by 0.5 px so there are no seams; the pieces are all
        # clockwise, so their concatenation fills correctly under nonzero.
        tree = shapely.STRtree(buf)
        x0, y0, x1, y1 = shapely.total_bounds(buf)
        tile = 120.0
        out = []
        for ty in np.arange(y0, y1, tile):
            for tx in np.arange(x0, x1, tile):
                box = shapely.box(tx - 0.5, ty - 0.5, tx + tile + 0.5, ty + tile + 0.5)
                idx = tree.query(box)
                if not len(idx):
                    continue
                u = shapely.union_all(shapely.intersection(buf[idx], box))
                if simplify:
                    u = u.simplify(simplify, preserve_topology=True)
                out.append(from_shape(u))
        return "".join(out)
    u = shapely.union_all(buf)
    if simplify:
        u = u.simplify(simplify, preserve_topology=True)
    return u if as_shape else from_shape(u)


def fillet(x, r: float, tol: float = TOL) -> str:
    """Round every corner of closed subpaths with radius ``r`` (convex and
    concave), keeping clockwise-on-screen orientation. Open subpaths pass
    through unchanged. Use before bending strip motifs round sharp corners."""
    out = []
    for pts, closed in as_polys(x, tol):
        if not closed or len(pts) < 3 or r <= 0:
            out.append(poly_d(pts, closed)); continue
        pg = Polygon(pts)
        if not pg.is_valid:
            pg = shapely.make_valid(pg)
        q = _qsegs(r) * 2
        pg = pg.buffer(-r, quad_segs=q).buffer(r, quad_segs=q)
        pg = pg.buffer(r, quad_segs=q).buffer(-r, quad_segs=q)
        for sub in ([pg] if pg.geom_type == "Polygon" else list(getattr(pg, "geoms", []))):
            if sub.is_empty:
                continue
            ring = np.asarray(sub.exterior.coords)[:-1]
            area = 0.5 * np.sum(ring[:, 0] * np.roll(ring[:, 1], -1) - np.roll(ring[:, 0], -1) * ring[:, 1])
            # keep the same winding sense as the input
            a_in = 0.5 * np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1])
            if np.sign(area) != np.sign(a_in):
                ring = ring[::-1]
            out.append(poly_d(ring, True))
    return "".join(out)


def simplify(x, tol: float = 0.05) -> str:
    """Douglas-Peucker simplify every subpath (curves are flattened first)."""
    out = []
    for pts, closed in as_polys(x, tol / 4):
        if len(pts) < 3:
            out.append(poly_d(pts, closed)); continue
        ls = LineString(np.vstack([pts, pts[:1]]) if closed else pts).simplify(tol, preserve_topology=False)
        c = np.asarray(ls.coords)
        if closed:
            c = c[:-1]
        out.append(poly_d(c, closed))
    return "".join(out)


def bbox(x) -> tuple[float, float, float, float]:
    """Tight bounds (x0, y0, x1, y1). Raises ValueError for empty geometry."""
    if _blank(x):
        raise ValueError("bbox() of empty geometry")
    if isinstance(x, str):
        b = to_skia(x, close=False).bounds
        return tuple(float(v) for v in b)
    polys = as_polys(x)
    if not polys:
        raise ValueError("bbox() of empty geometry")
    pts = np.vstack([p for p, _ in polys])
    return (float(pts[:, 0].min()), float(pts[:, 1].min()), float(pts[:, 0].max()), float(pts[:, 1].max()))


def area(x, fill_rule="nonzero") -> float:
    return float(to_shape(x, fill_rule).area)


# =============================================================================
# affine transforms (curves preserved for d-strings)
# =============================================================================
def _apply(M, xs, ys):
    a, b, c, d, e, f = M
    return a * xs + c * ys + e, b * xs + d * ys + f


def _is_point_list(x) -> bool:
    if not isinstance(x, (list, tuple)) or not x:
        return False
    if len(x) == 2 and isinstance(x[1], (bool, np.bool_)):
        return False
    f = x[0]
    return (isinstance(f, (list, tuple, np.ndarray)) and len(f) == 2 and
            isinstance(f[0], (int, float, np.floating, np.integer)))


def transform(x, M):
    """Apply SVG matrix (a,b,c,d,e,f): x' = a x + c y + e, y' = b x + d y + f.
    d-string -> d-string (curves kept); (N,2) array or a plain list of points
    -> (N,2) array; shapely -> shapely; Curve -> Curve; any other list of
    pathlikes -> [(points, closed), ...]."""
    if _is_point_list(x):
        x = np.asarray(x, float)
    if isinstance(x, str):
        out = []
        for c in parse_d(x):
            if c[0] == "Z":
                out.append(c); continue
            v = list(c[1:])
            for j in range(0, len(v), 2):
                v[j], v[j + 1] = _apply(M, v[j], v[j + 1])
            out.append((c[0], *v))
        if M[0] * M[3] - M[1] * M[2] < 0:
            # a reflection flips winding: reverse CLOSED subpaths so FILL art
            # keeps the clockwise convention (open centrelines keep direction)
            return "".join(reverse(cmds_to_d(sub)) if sub[-1][0] == "Z" else cmds_to_d(sub)
                           for sub in _split_subpaths(out))
        return cmds_to_d(out)
    if isinstance(x, np.ndarray):
        X, Y = _apply(M, x[:, 0], x[:, 1])
        return np.column_stack([X, Y])
    if isinstance(x, shapely.Geometry):
        a, b, c, d, e, f = M
        return shapely.affinity.affine_transform(x, [a, c, b, d, e, f])
    if isinstance(x, Curve):
        return Curve(transform(x.pts, M), x.closed)
    if isinstance(x, (list, tuple)):
        polys = as_polys(x)
        return [(transform(p, M), c) for p, c in polys]
    raise TypeError(type(x))


def translate(x, dx: float, dy: float = 0.0):
    return transform(x, (1, 0, 0, 1, dx, dy))


def rotate(x, deg: float, cx: float = 0.0, cy: float = 0.0):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return transform(x, (c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy))


def scale(x, sx: float, sy: float | None = None, cx: float = 0.0, cy: float = 0.0):
    sy = sx if sy is None else sy
    return transform(x, (sx, 0, 0, sy, cx - sx * cx, cy - sy * cy))


def mirror_x(x, axis: float = 375.0):
    """Flip horizontally about the vertical line x = axis (bilateral symmetry).
    Closed subpaths of d-strings are re-wound so FILL art stays clockwise."""
    return transform(x, (-1, 0, 0, 1, 2 * axis, 0))


def mirror_y(x, axis: float = 525.0):
    """Flip vertically about the horizontal line y = axis."""
    return transform(x, (1, 0, 0, -1, 0, 2 * axis))


def mirror_line(x, p=(0.0, 0.0), angle_deg: float = 45.0):
    """Reflect across the line through ``p`` at ``angle_deg`` (screen degrees)."""
    a = math.radians(2 * angle_deg)
    c, s = math.cos(a), math.sin(a)
    px, py = p
    # reflection matrix [[c, s],[s,-c]] about origin, conjugated by translation
    return transform(x, (c, s, s, -c, px - c * px - s * py, py - s * px + c * py))


def rotate180(x, cx: float = 375.0, cy: float = 525.0):
    """Rotate 180 degrees about the card centre (two-headed courts)."""
    return transform(x, (-1, 0, 0, -1, 2 * cx, 2 * cy))


def repeat_rotational(x, n: int, cx: float = 0.0, cy: float = 0.0, start_deg: float = 0.0) -> str:
    """n-fold rotational copies about (cx, cy); returns one d."""
    d = x if isinstance(x, str) else polys_d(x)
    return "".join(rotate(d, start_deg + 360.0 * k / n, cx, cy) for k in range(n))


def reverse(d: str) -> str:
    """Reverse the direction of every subpath (keeps curves)."""
    cmds = parse_d(d)
    subs = []
    cur = []
    for c in cmds:
        if c[0] == "M":
            if cur:
                subs.append(cur)
            cur = [c]
        else:
            cur.append(c)
    if cur:
        subs.append(cur)
    out = []
    for s in subs:
        closed = s[-1][0] == "Z"
        body = [c for c in s if c[0] != "Z"]
        # list of (segment, start point)
        pts = [(body[0][1], body[0][2])]
        segs = []
        for c in body[1:]:
            segs.append(c)
            pts.append((c[-2], c[-1]))
        if closed and pts[-1] != pts[0]:
            segs.append(("L", *pts[0]))
            pts.append(pts[0])
        rev = [("M", *pts[-1])]
        for k in range(len(segs) - 1, -1, -1):
            c = segs[k]
            p0 = pts[k]
            if c[0] == "L":
                rev.append(("L", *p0))
            elif c[0] == "C":
                rev.append(("C", c[3], c[4], c[1], c[2], *p0))
            elif c[0] == "Q":
                rev.append(("Q", c[1], c[2], *p0))
        if closed:
            rev.append(("Z",))
        out += rev
    return cmds_to_d(out)


def bilateral(x, axis: float = 375.0) -> str:
    """x plus its mirror about x=axis (closed subpaths keep their winding)."""
    d = x if isinstance(x, str) else polys_d(x)
    return d + mirror_x(d, axis)


# =============================================================================
# arc-length curves
# =============================================================================
class Curve:
    """Arc-length parametrised polyline.

    c = Curve(points_or_d); c.length; c.at(t) / c.at_s(s); c.tangent(t);
    c.normal(t) (left of travel on screen); c.resample(spacing); c.sample(n);
    c.sub(t0, t1); c.offset(dist_or_array); c.reversed().
    ``t`` is the arc-length fraction in [0, 1] (vectorised).
    """

    def __init__(self, x, closed: bool | None = None, tol: float = 0.02):
        if isinstance(x, Curve):
            pts, cl = x.pts, x.closed
        elif isinstance(x, np.ndarray) and x.ndim == 2:
            pts, cl = x.astype(float), False
        else:
            polys = as_polys(x, tol)
            if not polys:
                raise ValueError("empty path")
            pts, cl = polys[0]
        if closed is not None:
            cl = closed
        pts = np.asarray(pts, float)
        # drop duplicate consecutive points
        if len(pts) > 1:
            keep = np.r_[True, np.any(np.abs(np.diff(pts, axis=0)) > 1e-9, axis=1)]
            pts = pts[keep]
        self.closed = bool(cl)
        self.pts = pts
        P = np.vstack([pts, pts[:1]]) if self.closed else pts
        self._P = P
        seg = np.hypot(*np.diff(P, axis=0).T) if len(P) > 1 else np.zeros(0)
        self._s = np.r_[0.0, np.cumsum(seg)]
        self.length = float(self._s[-1])

    def at_s(self, s):
        s = np.asarray(s, float)
        if self.closed:
            s = np.mod(s, self.length)
        else:
            s = np.clip(s, 0, self.length)
        x = np.interp(s, self._s, self._P[:, 0])
        y = np.interp(s, self._s, self._P[:, 1])
        return np.stack([x, y], axis=-1)

    def at(self, t):
        return self.at_s(np.asarray(t, float) * self.length)

    def tangent_s(self, s, h: float | None = None):
        h = h if h is not None else max(0.25, min(2.0, self.length * 1e-3))
        s = np.asarray(s, float)
        if self.closed:
            a, b = s - h, s + h
        else:
            a = np.clip(s - h, 0, self.length)
            b = np.clip(s + h, 0, self.length)
        d = self.at_s(b) - self.at_s(a)
        n = np.hypot(d[..., 0], d[..., 1])[..., None]
        return d / np.where(n == 0, 1, n)

    def tangent(self, t, h=None):
        return self.tangent_s(np.asarray(t, float) * self.length, h)

    def normal(self, t, h=None):
        T = self.tangent(t, h)
        return np.stack([T[..., 1], -T[..., 0]], axis=-1)

    def normal_s(self, s, h=None):
        T = self.tangent_s(s, h)
        return np.stack([T[..., 1], -T[..., 0]], axis=-1)

    def angle(self, t):
        """Direction of travel in degrees (screen coords)."""
        T = self.tangent(t)
        return np.degrees(np.arctan2(T[..., 1], T[..., 0]))

    def sample(self, n: int) -> np.ndarray:
        t = np.linspace(0, 1, n, endpoint=not self.closed)
        return self.at(t)

    def resample(self, spacing: float, keep_corners: float | None = None) -> np.ndarray:
        """Even arc-length samples (endpoints kept). ``keep_corners`` = turn angle
        in degrees above which original vertices are preserved exactly."""
        n = max(2, int(math.ceil(self.length / max(spacing, 1e-6))) + 1)
        if keep_corners is None or len(self.pts) < 3:
            return self.sample(n) if not self.closed else self.at(np.linspace(0, 1, n)[:-1])
        P = self._P
        v1 = P[1:-1] - P[:-2]
        v2 = P[2:] - P[1:-1]
        ang = np.degrees(np.abs(np.arctan2(v1[:, 0] * v2[:, 1] - v1[:, 1] * v2[:, 0],
                                           (v1 * v2).sum(1))))
        corners = np.where(ang > keep_corners)[0] + 1
        cuts = np.r_[0.0, self._s[corners], self.length]
        out = []
        for a, b in zip(cuts[:-1], cuts[1:]):
            m = max(1, int(math.ceil((b - a) / spacing)))
            out.append(self.at_s(np.linspace(a, b, m + 1)[:-1]))
        out.append(self.at_s([self.length]))
        res = np.vstack(out)
        if self.closed:
            res = res[:-1]
        return res

    def sub(self, t0: float, t1: float, spacing: float | None = None) -> "Curve":
        """Piece between arc fractions t0..t1 (open curve). On closed curves
        t1 < t0 wraps across the seam; on open curves it raises."""
        L = self.length
        s0, s1 = t0 * L, t1 * L
        if s1 < s0:
            if not self.closed:
                raise ValueError("Curve.sub: t1 < t0 on an open curve")
            s1 += L
        if self.closed and L:
            k0 = math.floor(s0 / L)
            base = np.concatenate([self._s[:-1] + k * L for k in (k0, k0 + 1, k0 + 2)])
            inner = base[(base > s0) & (base < s1)]
        else:
            inner = self._s[(self._s > s0) & (self._s < s1)]
        s = np.r_[s0, inner, s1]
        return Curve(self.at_s(s))

    def offset(self, dist, spacing: float | None = None) -> np.ndarray:
        """Points offset along the left normal; ``dist`` scalar or callable(t)."""
        sp = spacing or max(0.5, self.length / 2000)
        n = max(2, int(self.length / sp) + 1)
        t = np.linspace(0, 1, n, endpoint=not self.closed)
        D = dist(t) if callable(dist) else np.full_like(t, float(dist))
        return self.at(t) + self.normal(t) * D[:, None]

    def map(self, uv) -> np.ndarray:
        """Strip mapping: local (u = arc length px, v = offset px along the left
        normal) -> page points. Design a motif on a straight strip, then bend it
        along any path (ropes, bands, borders). Closed curves wrap u."""
        uv = np.asarray(uv, float)
        P = self.at_s(uv[..., 0])
        Nn = self.normal_s(uv[..., 0])
        return P + Nn * uv[..., 1:2]

    def reversed(self) -> "Curve":
        return Curve(self.pts[::-1].copy(), self.closed)

    def d(self) -> str:
        return poly_d(self.pts, self.closed)


def curve(x, closed=None) -> Curve:
    return x if isinstance(x, Curve) and closed is None else Curve(x, closed)


def resample(x, spacing: float, keep_corners: float | None = None) -> np.ndarray:
    """Even arc-length resample of the first subpath of ``x``."""
    return curve(x).resample(spacing, keep_corners)


def point_at(x, t):
    return curve(x).at(t)


def tangent_at(x, t):
    return curve(x).tangent(t)


def normal_at(x, t):
    return curve(x).normal(t)


# =============================================================================
# smooth curves and primitives
# =============================================================================
def smooth_d(points, closed: bool = False, tension: float = 0.5) -> str:
    """Centripetal-ish Catmull-Rom spline through points, as cubic béziers.
    ``tension`` 0.5 = standard Catmull-Rom (1/6 handle factor * 3 = 0.5)."""
    P = np.asarray(points, float)
    n = len(P)
    if n < 2:
        return ""
    if n == 2:
        return poly_d(P)
    k = tension / 3.0
    cmds = [("M", *P[0])]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[0] * 2 - P[1]
        p1 = P[i]
        p2 = P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else P[-1] * 2 - P[-2]
        c1 = p1 + (p2 - p0) * k
        c2 = p2 - (p3 - p1) * k
        cmds.append(("C", *c1, *c2, *p2))
    if closed:
        cmds.append(("Z",))
    return cmds_to_d(cmds)


def spline(points, closed: bool = False, tension: float = 0.5, tol: float = 0.02) -> np.ndarray:
    """Dense polyline of the Catmull-Rom spline through points."""
    polys = flatten(smooth_d(points, closed, tension), tol)
    return polys[0][0] if polys else np.asarray(points, float)


def arc_pts(cx, cy, r, a0_deg, a1_deg, n: int | None = None, ry: float | None = None) -> np.ndarray:
    """Points on a circular/elliptic arc from a0 to a1 (degrees, screen coords)."""
    ry = r if ry is None else ry
    if n is None:
        span = abs(math.radians(a1_deg - a0_deg))
        n = max(2, int(span * max(r, ry) / 1.0) + 2, int(span / 0.05) + 2)
    a = np.radians(np.linspace(a0_deg, a1_deg, n))
    return np.column_stack([cx + r * np.cos(a), cy + ry * np.sin(a)])


def circle_d(cx, cy, r) -> str:
    """Circle as two arcs (exact), clockwise on screen (FILL convention)."""
    from .svg import fmt
    if not (math.isfinite(r) and r > 0):
        raise ValueError(f"circle_d: radius must be > 0, got {r!r}")
    return (f"M{fmt(cx - r)} {fmt(cy)}a{fmt(r)} {fmt(r)} 0 1 1 {fmt(2 * r)} 0"
            f"a{fmt(r)} {fmt(r)} 0 1 1 {fmt(-2 * r)} 0z")


def ellipse_d(cx, cy, rx, ry, rot_deg: float = 0.0) -> str:
    from .svg import fmt
    if not (rx > 0 and ry > 0):
        raise ValueError(f"ellipse_d: radii must be > 0, got {rx!r}, {ry!r}")
    d = (f"M{fmt(cx - rx)} {fmt(cy)}a{fmt(rx)} {fmt(ry)} 0 1 1 {fmt(2 * rx)} 0"
         f"a{fmt(rx)} {fmt(ry)} 0 1 1 {fmt(-2 * rx)} 0z")
    return rotate(d, rot_deg, cx, cy) if rot_deg else d


def rect_d(x, y, w, h, r: float = 0.0) -> str:
    """(Rounded) rectangle, clockwise on screen."""
    from .svg import fmt
    if r <= 0:
        return f"M{fmt(x)} {fmt(y)}h{fmt(w)}v{fmt(h)}h{fmt(-w)}z"
    r = min(r, w / 2, h / 2)
    k = 0.5522847498 * r
    cmds = [("M", x + r, y), ("L", x + w - r, y),
            ("C", x + w - r + k, y, x + w, y + r - k, x + w, y + r), ("L", x + w, y + h - r),
            ("C", x + w, y + h - r + k, x + w - r + k, y + h, x + w - r, y + h), ("L", x + r, y + h),
            ("C", x + r - k, y + h, x, y + h - r + k, x, y + h - r), ("L", x, y + r),
            ("C", x, y + r - k, x + r - k, y, x + r, y), ("Z",)]
    return cmds_to_d(cmds)


def polygon_d(cx, cy, r, n: int, rot_deg: float = -90.0) -> str:
    """Regular n-gon (clockwise on screen)."""
    if n < 3:
        raise ValueError("polygon_d needs n >= 3")
    a = np.radians(rot_deg + np.arange(n) * 360.0 / n)
    return poly_d(np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a)]), True, orient="cw")


def star_d(cx, cy, r_out, r_in, n: int, rot_deg: float = -90.0) -> str:
    """n-pointed star (clockwise on screen)."""
    if n < 2:
        raise ValueError("star_d needs n >= 2")
    a = np.radians(rot_deg + np.arange(2 * n) * 180.0 / n)
    rr = np.where(np.arange(2 * n) % 2 == 0, r_out, r_in)
    return poly_d(np.column_stack([cx + rr * np.cos(a), cy + rr * np.sin(a)]), True, orient="cw")


# =============================================================================
# knockouts, interlace, junction fillets
# =============================================================================
def knockout(art, occluder, gap: float = 1.5, *, lines: bool = False, lw: float = 0.0,
             cap: str = "round") -> str:
    """Hide ``art`` where ``occluder`` (a FILL shape drawn on top) sits, leaving
    a clear ``gap`` px round it — a geometric knockout that survives print
    separation (no paper-coloured cover needed).

    FILL art (default): ``art − offset(occluder, gap)`` -> FILL d.
    STROKE art (``lines=True``): centrelines are cut so that, drawn at width
    ``lw`` with ``cap`` caps, they stop ``gap`` px short of the occluder
    -> STROKE d (feed to :func:`inkkit.hatch.lines_of` / ``hatch.emit`` to taper)."""
    if _blank(art):
        return ""
    if _blank(occluder):
        return art if isinstance(art, str) else polys_d(art)
    occ = to_shape(occluder)
    if lines:
        reach = gap + (lw / 2 if cap == "round" else 0.0)
        return clip_out(art, occ.buffer(reach, quad_segs=_qsegs(reach)) if reach > 0 else occ)
    return difference(art, from_shape(occ.buffer(gap, quad_segs=_qsegs(gap))) if gap > 0 else from_shape(occ))


def fillet_junction(x, point, r: float = 1.5, reach: float | None = None) -> str:
    """Fill the V crotch where two FILL strokes meet near ``point`` with a
    concave fillet of radius ``r`` (a morphological close restricted to a disc
    of radius ``reach``, default 4r, round the junction). -> FILL d."""
    s = to_shape(x)
    if s.is_empty or r <= 0:
        return from_shape(s)
    q = _qsegs(r) * 2
    closed = s.buffer(r, quad_segs=q).buffer(-r, quad_segs=q)
    zone = shapely.Point(point).buffer(reach if reach is not None else 4 * r, quad_segs=16)
    add = closed.difference(s).intersection(zone)
    return from_shape(s.union(add)) if not add.is_empty else from_shape(s)


def _seg_intersections(A: np.ndarray, B: np.ndarray, same: bool, closed: bool):
    """Crossings between polyline A and polyline B (vertices (n,2)); returns a
    list of (ia, ta, ib, tb, point) with segment indices and fractions."""
    a0, a1 = A[:-1], A[1:]
    b0, b1 = B[:-1], B[1:]
    boxes_b = shapely.box(np.minimum(b0[:, 0], b1[:, 0]), np.minimum(b0[:, 1], b1[:, 1]),
                          np.maximum(b0[:, 0], b1[:, 0]), np.maximum(b0[:, 1], b1[:, 1]))
    boxes_a = shapely.box(np.minimum(a0[:, 0], a1[:, 0]), np.minimum(a0[:, 1], a1[:, 1]),
                          np.maximum(a0[:, 0], a1[:, 0]), np.maximum(a0[:, 1], a1[:, 1]))
    tree = shapely.STRtree(boxes_b)
    ia, ib = tree.query(boxes_a, predicate="intersects")
    if same:
        nseg = len(a0)
        keep = np.abs(ia - ib) > 1
        if closed:
            keep &= ~(((ia == 0) & (ib == nseg - 1)) | ((ib == 0) & (ia == nseg - 1)))
        keep &= ia < ib
        ia, ib = ia[keep], ib[keep]
    if not len(ia):
        return []
    p, r = a0[ia], a1[ia] - a0[ia]
    q, s = b0[ib], b1[ib] - b0[ib]
    rxs = r[:, 0] * s[:, 1] - r[:, 1] * s[:, 0]
    qp = q - p
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (qp[:, 0] * s[:, 1] - qp[:, 1] * s[:, 0]) / rxs
        u = (qp[:, 0] * r[:, 1] - qp[:, 1] * r[:, 0]) / rxs
    ok = (np.abs(rxs) > 1e-12) & (t >= 0) & (t < 1) & (u >= 0) & (u < 1)
    out = []
    for k in np.where(ok)[0]:
        out.append((int(ia[k]), float(t[k]), int(ib[k]), float(u[k]), p[k] + t[k] * r[k]))
    return out


def interlace(strands, width: float = 2.1, gap: float = 4.2, *, over="alternate",
              cap: str = "round", as_lines: bool = False, closed=None, spacing: float = 0.5):
    """Monoline interlace (knotwork / over-under ribbons).

    ``strands`` is a list of centrelines (d-strings, point arrays, Curves; a
    single pathlike with several subpaths also works). Every crossing —
    between strands and a strand with itself — is found; the UNDER strand is
    broken so that, drawn at ``width`` with ``cap`` caps, it stops ``gap`` px
    clear of each side of the OVER strand.

    over  'alternate' (default) — crossings alternate over/under along each
          strand as in knotwork; 'order' — earlier strands pass over later
          ones; or callable(i, j, point) -> True when strand i is over j.
    Returns FILL d (outlined at ``width``), or STROKE centrelines with
    ``as_lines=True``."""
    if isinstance(strands, (str, Curve)) or (isinstance(strands, np.ndarray) and strands.ndim == 2):
        strands = [strands]
    curves = []
    for st in strands:
        for pts, cl in as_polys(st, 0.02):
            if len(pts) >= 2:
                cv = Curve(pts, cl if closed is None else closed)
                if cv.length > 0:
                    curves.append(Curve(cv.resample(spacing), cv.closed))
    if not curves:
        return ""
    polys = [np.vstack([c.pts, c.pts[:1]]) if c.closed else c.pts for c in curves]
    svals = [np.r_[0.0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))] for P in polys]
    # --- find crossings -------------------------------------------------------
    xs = []  # (i, s_i, j, s_j, point)
    for i in range(len(polys)):
        for j in range(i, len(polys)):
            for ia, ta, ib, tb, pt in _seg_intersections(polys[i], polys[j], i == j, curves[i].closed):
                si = svals[i][ia] + ta * (svals[i][ia + 1] - svals[i][ia])
                sj = svals[j][ib] + tb * (svals[j][ib + 1] - svals[j][ib])
                xs.append([i, si, j, sj, pt])
    # --- decide over/under ------------------------------------------------------
    top = {}  # crossing index -> (strand, s) that is OVER
    if callable(over):
        for k, (i, si, j, sj, pt) in enumerate(xs):
            top[k] = (i, si) if over(i, j, pt) else (j, sj)
    elif over == "order":
        for k, (i, si, j, sj, pt) in enumerate(xs):
            top[k] = (i, min(si, sj)) if i == j else (i, si)
    elif over == "alternate":
        events = {}
        for k, (i, si, j, sj, pt) in enumerate(xs):
            events.setdefault(i, []).append((si, k, 0))
            events.setdefault(j, []).append((sj, k, 1))
        for st in range(len(polys)):
            ev = sorted(events.get(st, []))
            state = None
            for s_, k, side in ev:
                i, si, j, sj, pt = xs[k]
                me = (i, si) if side == 0 else (j, sj)
                if k in top:
                    state = top[k] == me
                else:
                    state = True if state is None else not state
                    top[k] = me if state else ((j, sj) if side == 0 else (i, si))
    else:
        raise ValueError("over must be 'alternate', 'order' or a callable")
    # --- cut under strands ---------------------------------------------------
    clear = width / 2 + gap + (width / 2 if cap == "round" else 0.0)
    cuts: dict[int, list] = {}
    for k, (i, si, j, sj, pt) in enumerate(xs):
        o_strand, o_s = top[k]
        if (o_strand, o_s) == (i, si):
            u_strand, u_s = j, sj
        else:
            u_strand, u_s = i, si
        oc = curves[o_strand]
        reach = 3 * clear + 2 * width
        lo, hi = o_s - reach, o_s + reach
        if not oc.closed:
            lo, hi = max(lo, 0.0), min(hi, oc.length)
        opts = oc.at_s(np.linspace(lo, hi, max(4, int((hi - lo) / spacing) + 1)))
        oline = LineString(opts)
        uc = curves[u_strand]
        ss = u_s + np.linspace(-reach, reach, max(8, int(2 * reach / (spacing / 2)) + 1))
        if not uc.closed:
            ss = np.clip(ss, 0, uc.length)
        up = uc.at_s(ss)
        dist = shapely.distance(oline, shapely.points(up[:, 0], up[:, 1]))
        mid = int(np.argmin(np.abs(ss - u_s)))
        a = mid
        while a > 0 and dist[a - 1] < clear:
            a -= 1
        b = mid
        while b < len(ss) - 1 and dist[b + 1] < clear:
            b += 1
        cuts.setdefault(u_strand, []).append((ss[a], ss[b]))
    # --- emit remaining pieces ---------------------------------------------------
    pieces = []
    for n, cv in enumerate(curves):
        L = cv.length
        iv = cuts.get(n, [])
        if not iv:
            pieces.append((cv.pts, cv.closed))
            continue
        if cv.closed:
            # rotate the parameter so that s=0 sits inside the first cut
            base = iv[0][0]
            rel = sorted(((a - base) % L, (a - base) % L + (b - a)) for a, b in iv)
            merged = []
            for a, b in rel:
                if merged and a <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], b)
                else:
                    merged.append([a, b])
            for (a0, b0), (a1, _) in zip(merged, merged[1:] + [[merged[0][0] + L, 0]]):
                if a1 - b0 > 1e-6:
                    s = np.linspace(base + b0, base + a1, max(2, int((a1 - b0) / spacing) + 1))
                    pieces.append((cv.at_s(s), False))
        else:
            merged = []
            for a, b in sorted(iv):
                if merged and a <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], b)
                else:
                    merged.append([a, b])
            edges = [0.0] + [v for ab in merged for v in ab] + [L]
            for a, b in zip(edges[0::2], edges[1::2]):
                if b - a > 1e-6:
                    s = np.linspace(a, b, max(2, int((b - a) / spacing) + 1))
                    pieces.append((cv.at_s(s), False))
    if as_lines:
        return polys_d(pieces)
    return outline(pieces, width, cap=cap)


# =============================================================================
# Bézier curve fitting (smaller, editable output)
# =============================================================================
def _bez_pt(b, u):
    u = u[:, None]
    mu = 1 - u
    return mu ** 3 * b[0] + 3 * mu * mu * u * b[1] + 3 * mu * u * u * b[2] + u ** 3 * b[3]


def _bez_d1(b, u):
    u = u[:, None]
    mu = 1 - u
    return 3 * (mu * mu * (b[1] - b[0]) + 2 * mu * u * (b[2] - b[1]) + u * u * (b[3] - b[2]))


def _bez_d2(b, u):
    u = u[:, None]
    return 6 * ((1 - u) * (b[2] - 2 * b[1] + b[0]) + u * (b[3] - 2 * b[2] + b[1]))


def _gen_bezier(P, u, t1, t2):
    p0, p3 = P[0], P[-1]
    mu = 1 - u
    B0, B1, B2, B3 = mu ** 3, 3 * mu * mu * u, 3 * mu * u * u, u ** 3
    A1 = t1[None, :] * B1[:, None]
    A2 = t2[None, :] * B2[:, None]
    C = np.array([[np.sum(A1 * A1), np.sum(A1 * A2)], [np.sum(A1 * A2), np.sum(A2 * A2)]])
    tmp = P - ((B0 + B1)[:, None] * p0 + (B2 + B3)[:, None] * p3)
    X = np.array([np.sum(A1 * tmp), np.sum(A2 * tmp)])
    det = C[0, 0] * C[1, 1] - C[0, 1] * C[1, 0]
    seg = float(np.hypot(*(p3 - p0)))
    if abs(det) > 1e-12:
        a1 = (X[0] * C[1, 1] - X[1] * C[0, 1]) / det
        a2 = (C[0, 0] * X[1] - C[1, 0] * X[0]) / det
    else:
        a1 = a2 = -1.0
    eps = 1e-6 * max(seg, 1e-9)
    if a1 < eps or a2 < eps or a1 > 1.5 * seg or a2 > 1.5 * seg:
        a1 = a2 = seg / 3.0
    return np.array([p0, p0 + t1 * a1, p3 + t2 * a2, p3])


def _curve_ok(b, P, tol):
    """Every point of the cubic lies within ``tol`` of the polyline P (catches
    loops and bulges between the fitted sample points)."""
    Q = _bez_pt(b, np.linspace(0, 1, max(12, min(3 * len(P), 200))))
    return float(shapely.distance(LineString(P), shapely.points(Q[:, 0], Q[:, 1])).max()) <= tol


def _fit_cubic(P, t1, t2, tol, depth=0):
    n = len(P)
    if n == 2:
        dist = float(np.hypot(*(P[1] - P[0]))) / 3
        return [np.array([P[0], P[0] + t1 * dist, P[1] + t2 * dist, P[1]])]
    seg = np.hypot(*np.diff(P, axis=0).T)
    u = np.r_[0.0, np.cumsum(seg)]
    u = u / u[-1] if u[-1] > 0 else np.linspace(0, 1, n)
    b = _gen_bezier(P, u, t1, t2)
    err = np.sum((_bez_pt(b, u) - P) ** 2, axis=1)
    tol2 = tol * tol
    if err.max() <= tol2 and _curve_ok(b, P, tol):
        return [b]
    if err.max() <= 16 * tol2:
        for _ in range(8):
            q, d1, d2 = _bez_pt(b, u) - P, _bez_d1(b, u), _bez_d2(b, u)
            num = np.sum(q * d1, axis=1)
            den = np.sum(d1 * d1, axis=1) + np.sum(q * d2, axis=1)
            with np.errstate(divide="ignore", invalid="ignore"):
                un = np.where(np.abs(den) > 1e-12, u - num / den, u)
            un = np.clip(un, 0, 1)
            un[0], un[-1] = 0.0, 1.0
            if np.any(np.diff(un) <= 0):
                break
            u = un
            b = _gen_bezier(P, u, t1, t2)
            err = np.sum((_bez_pt(b, u) - P) ** 2, axis=1)
            if err.max() <= tol2 and _curve_ok(b, P, tol):
                return [b]
    if depth > 40:
        return [np.array([P[k], P[k] + (P[k + 1] - P[k]) / 3, P[k + 1] - (P[k + 1] - P[k]) / 3, P[k + 1]])
                for k in range(n - 1)]
    if err.max() <= tol2:      # sample points fit but the curve bulges between them
        split = n // 2
    else:
        split = int(np.clip(np.argmax(err[1:-1]) + 1, 1, n - 2))
    tc = P[split - 1] - P[split + 1]
    nc = float(np.hypot(*tc))
    tc = tc / nc if nc > 1e-12 else np.array([1.0, 0.0])
    return (_fit_cubic(P[:split + 1], t1, tc, tol, depth + 1) +
            _fit_cubic(P[split:], -tc, t2, tol, depth + 1))


def _unit(v):
    n = float(np.hypot(*v))
    return v / n if n > 1e-12 else np.array([1.0, 0.0])


def _densify_pts(P, step):
    out = [P[:1]]
    for a, b in zip(P[:-1], P[1:]):
        L = float(np.hypot(*(b - a)))
        k = max(1, int(math.ceil(L / step)))
        out.append(a + np.outer(np.arange(1, k + 1) / k, b - a))
    return np.vstack(out)


def _fit_run(P, tol, corner, periodic):
    """Fit a polyline run; returns ('C', ...) / ('L', ...) commands. With
    ``periodic`` the run is a whole closed ring (P[0] == P[-1]) and a smooth
    seam keeps a continuous tangent."""
    P = np.asarray(P, float)
    keep = np.r_[True, np.any(np.abs(np.diff(P, axis=0)) > 1e-9, axis=1)]
    P = P[keep]
    if len(P) < 3:
        return [("L", *p) for p in P[1:]]
    v = np.diff(P, axis=0)
    ang = np.degrees(np.abs(np.arctan2(v[:-1, 0] * v[1:, 1] - v[:-1, 1] * v[1:, 0],
                                       np.sum(v[:-1] * v[1:], axis=1))))
    seam_smooth = False
    if periodic and len(P) > 3:
        a0 = math.degrees(abs(math.atan2(v[-1, 0] * v[0, 1] - v[-1, 1] * v[0, 0], float(v[-1] @ v[0]))))
        seam_smooth = a0 <= corner
    cut = [0] + [int(k) + 1 for k in np.where(ang > corner)[0]] + [len(P) - 1]
    cmds = []
    for a, b in zip(cut[:-1], cut[1:]):
        R = P[a:b + 1]
        if len(R) < 5:          # short runs are cheaper as straight segments
            cmds.extend(("L", *q) for q in R[1:])
            continue
        D = _densify_pts(R, 2.0)
        # start tangent: one-sided at corners / open ends, centred elsewhere
        if a == 0:
            t1 = _unit(P[1] - P[-2]) if seam_smooth else _unit(D[min(2, len(D) - 1)] - D[0])
        else:
            t1 = _unit(D[min(2, len(D) - 1)] - D[0])
        if b == len(P) - 1:
            t2 = -_unit(P[1] - P[-2]) if seam_smooth else _unit(D[max(-3, -len(D))] - D[-1])
        else:
            t2 = _unit(D[max(-3, -len(D))] - D[-1])
        for bz in _fit_cubic(D, t1, t2, tol):
            cmds.append(("C", *bz[1], *bz[2], *bz[3]))
    return cmds


def fit_curves(x, tol: float = 0.05, corner: float = 40.0, min_run: int = 5) -> str:
    """Replace dense polyline runs with fitted cubic Béziers (Schneider's
    algorithm, corners kept where the polyline turns more than ``corner``°).
    Existing curve segments pass through untouched. Deviation stays below
    ``tol`` px (checked along the whole curve). Shrinks dense polyline art
    1.2–3.5× (smooth guilloché the most)
    and makes it practical to hand-finish in Illustrator/Inkscape."""
    d = x if isinstance(x, str) else polys_d(x)
    if not d.strip():
        return ""
    out = []
    for sub in _split_subpaths(parse_d(d)):
        closed = sub[-1][0] == "Z"
        body = [c for c in sub if c[0] != "Z"]
        res = [body[0]]
        run = [body[0][1:3]] if body[0][0] == "M" else []
        cur = np.array(body[0][1:3]) if body[0][0] == "M" else None

        def flush(run, closing=False):
            if len(run) >= min_run:
                res.extend(_fit_run(np.array(run), tol, corner, closing))
            else:
                res.extend(("L", *p) for p in run[1:])

        for c in body[1:]:
            if c[0] == "L":
                run.append(c[1:3])
            else:
                flush(run)
                res.append(c)
                run = [c[-2:]]
        if closed and run:
            start = body[0][1:3]
            if not np.allclose(run[-1], start):
                run.append(start)
            whole = all(c[0] == "L" for c in body[1:])  # the ring is one polyline run
            flush(run, closing=whole)
            res.append(("Z",))
        else:
            flush(run)
        out.append(cmds_to_d(res))
    return "".join(out)


def round_corners(x, r: float, min_angle: float = 12.0, tol: float = TOL) -> str:
    """Replace every polyline corner that turns more than ``min_angle``° with a
    tangent circular arc of radius ``r`` (shrunk where the adjacent segments
    are too short). Works on open and closed subpaths alike — use it before
    bending strip motifs (guilloché, bands) round sharp corners. -> d."""
    if not r > 0:
        raise ValueError("round_corners: r must be > 0")
    out = []
    for pts, closed in as_polys(x, tol):
        P = np.asarray(pts, float)
        n = len(P)
        if n < 3:
            out.append(poly_d(P, closed))
            continue
        idx = range(n) if closed else range(1, n - 1)
        new = []
        if not closed:
            new.append(P[0])
        for i in idx:
            a, b, c = P[i - 1], P[i], P[(i + 1) % n]
            v1, v2 = b - a, c - b
            l1, l2 = float(np.hypot(*v1)), float(np.hypot(*v2))
            if l1 < 1e-9 or l2 < 1e-9:
                new.append(b)
                continue
            u1, u2 = v1 / l1, v2 / l2
            turn = math.atan2(u1[0] * u2[1] - u1[1] * u2[0], float(u1 @ u2))
            if abs(math.degrees(turn)) < min_angle:
                new.append(b)
                continue
            tl = r * math.tan(abs(turn) / 2)
            lim = 0.5 * min(l1, l2)
            rr = r if tl <= lim else lim / math.tan(abs(turn) / 2)
            tl = min(tl, lim)
            p1 = b - u1 * tl
            nrm = np.array([-u1[1], u1[0]]) * (1 if turn > 0 else -1)
            ctr = p1 + nrm * rr
            a0 = math.atan2(p1[1] - ctr[1], p1[0] - ctr[0])
            k = max(2, int(math.ceil(abs(turn) / (2 * math.acos(max(-1.0, 1 - tol / max(rr, tol)))))) + 1)
            ang = a0 + np.linspace(0, turn, k)
            new.extend(np.column_stack([ctr[0] + rr * np.cos(ang), ctr[1] + rr * np.sin(ang)]))
        if not closed:
            new.append(P[-1])
        out.append(poly_d(np.asarray(new), closed))
    return "".join(out)
