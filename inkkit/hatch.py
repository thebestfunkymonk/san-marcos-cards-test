"""Engraving fills clipped to any shape.

Return conventions (see each docstring):
* STROKE d  -> open centrelines; draw with ``stroke=<ink> stroke-width=<w> fill=none``
  (use ``stroke-linecap=round``, or ``butt`` for hatch that meets a contour).
  Pass ``width=`` to get FILL outlines instead.
* FILL d    -> closed, clockwise outlines (tonal engraving, stipple, dot
  screens, tapered hatch).

Shapes are any pathlike (d-string, points, shapely geometry). Lines are clipped
exactly (shapely line/polygon intersection), so ends sit precisely on the edge;
``taper=`` makes each line fade over that many px at both ends (down to
``min_width``, finishing in a round cap). Every generator returns '' for an
empty region (e.g. a shape consumed by ``inset=``).
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np
import shapely
from shapely.geometry import LineString, MultiLineString

from . import geom as G
from .stroke import ease, variable_stroke

__all__ = ["parallel", "cross", "contour", "concentric", "radial", "flow", "along", "between",
           "half", "latitudes", "engrave", "tonal", "stipple", "dot_screen", "lines_of", "emit",
           "sphere_tone", "linear_tone", "radial_tone", "cylinder_tone", "bevel_tone",
           "shape_distance_tone", "clamp_tone"]


# =============================================================================
# helpers
# =============================================================================
def _region(shape, fill_rule="nonzero"):
    if isinstance(shape, shapely.Geometry):
        gm = shape
    else:
        gm = G.to_shape(shape, fill_rule)
    if not gm.is_empty and not gm.is_valid:
        gm = shapely.make_valid(gm)
    return gm


def _positive(name, v):
    if not (v is not None and math.isfinite(v) and v > 0):
        raise ValueError(f"{name} must be > 0, got {v!r}")


def _choice(name, v, allowed):
    if v not in allowed:
        raise ValueError(f"{name} must be one of {allowed}, not {v!r}")


def _lines_from_geom(gm) -> list[np.ndarray]:
    out = []
    if gm.is_empty:
        return out
    if isinstance(gm, LineString):
        c = np.asarray(gm.coords)
        if len(c) >= 2:
            out.append(c)
    elif hasattr(gm, "geoms"):
        for g in gm.geoms:
            out += _lines_from_geom(g)
    return out


def _clip(lines: list[np.ndarray], region, min_len=0.0) -> list[np.ndarray]:
    if not lines or region.is_empty:
        return []
    geoms = [LineString(l) for l in lines if len(l) >= 2]
    res = shapely.intersection(MultiLineString(geoms), region)
    try:
        res = shapely.line_merge(res)
    except Exception:
        pass
    out = _lines_from_geom(res)
    if min_len > 0:
        out = [l for l in out if np.hypot(*np.diff(l, axis=0).T).sum() >= min_len]
    return out


def lines_of(x) -> list[np.ndarray]:
    """Any pathlike -> list of polylines (closed ones get their first point appended)."""
    out = []
    for p, c in G.as_polys(x, 0.02):
        out.append(np.vstack([p, p[:1]]) if c else p)
    return out


def emit(lines, width=None, taper=0.0, cap="round", power=1.0, min_width=0.0,
         taper_ends=None) -> str:
    """Polylines -> STROKE d, or FILL d when ``width`` is given.

    taper      px over which each line fades at its ends (to ``min_width``)
    cap        'round' | 'butt' (butt: hatch that meets a contour's centreline)
    taper_ends optional list of (taper_start, taper_end) booleans per line."""
    lines = [np.asarray(l, float) for l in lines]
    if width is None:
        return "".join(G.poly_d(l) for l in lines if len(l) >= 2)
    _positive("width", width)
    _choice("cap", cap, ("round", "butt", "flat"))
    out = []
    r0 = width / 2
    for k, l in enumerate(lines):
        if len(l) < 2:
            continue
        cv = G.Curve(l)
        if cv.length < 1e-6:
            continue
        P = cv.resample(min(0.8, max(0.25, width)), keep_corners=25)
        seg = np.hypot(*np.diff(P, axis=0).T)
        s = np.r_[0.0, np.cumsum(seg)]
        R = np.full(len(P), r0)
        ts, te = (True, True) if taper_ends is None else taper_ends[k]
        if taper and taper > 0:
            tl = min(taper, s[-1] / 2)
            f = np.ones_like(s)
            if ts:
                f = f * ease(s / tl, power)
            if te:
                f = f * ease((s[-1] - s) / tl, power)
            R = R * f
        if min_width:
            R = np.maximum(R, min_width / 2)
        c = "flat" if cap in ("butt", "flat") else "round"
        sc = "round" if (taper and ts) else c
        ec = "round" if (taper and te) else c
        out.append(variable_stroke(P, R, start_cap=sc, end_cap=ec))
    return "".join(out)


_emit = emit  # backwards-compatible private name


def _parallel_lines(region, angle, spacing, offset=0.0):
    x0, y0, x1, y1 = region.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + spacing
    a = math.radians(angle)
    u = np.array([math.cos(a), math.sin(a)])       # line direction
    v = np.array([-math.sin(a), math.cos(a)])      # step direction
    k0 = math.floor((-R - offset) / spacing)
    k1 = math.ceil((R - offset) / spacing)
    lines = []
    for k in range(k0, k1 + 1):
        o = k * spacing + offset
        c = np.array([cx, cy]) + v * o
        lines.append(np.array([c - u * R, c + u * R]))
    return lines


# =============================================================================
# hatch generators
# =============================================================================
def parallel(shape, angle: float = 45.0, spacing: float = 4.0, *, offset: float = 0.0,
             width: float | None = None, taper: float = 0.0, inset: float = 0.0,
             min_len: float = 0.0, cap: str = "round", min_width: float = 0.0,
             fill_rule: str = "nonzero") -> str:
    """Parallel hatch at ``angle`` degrees, ``spacing`` px apart.
    -> STROKE d, or FILL d if ``width`` (``taper`` px fades each line end)."""
    _positive("spacing", spacing)
    region = _region(shape, fill_rule)
    if inset and not region.is_empty:
        region = region.buffer(-inset)
    if region.is_empty:
        return ""
    lines = _clip(_parallel_lines(region, angle, spacing, offset), region, min_len)
    return emit(lines, width, taper, cap=cap, min_width=min_width)


def cross(shape, angles=(45.0, -45.0), spacing: float = 4.0, **kw) -> str:
    """Cross-hatch: parallel hatch at each angle. Same return rules as parallel()."""
    return "".join(parallel(shape, a, spacing, **kw) for a in angles)


def _side_pieces(region, divider, side):
    """Split ``region`` by the (extended) divider polyline; return the part on
    ``side`` (+1 left of the divider's direction on screen, -1 right)."""
    from shapely.ops import split
    P = G.curve(divider).pts
    x0, y0, x1, y1 = region.bounds
    ext = math.hypot(x1 - x0, y1 - y0) + 10
    t0 = P[0] - P[1]
    t1 = P[-1] - P[-2]
    P = np.vstack([P[0] + t0 / max(np.hypot(*t0), 1e-9) * ext, P,
                   P[-1] + t1 / max(np.hypot(*t1), 1e-9) * ext])
    line = LineString(P)
    pieces = split(region, line)
    keep = []
    for pc in getattr(pieces, "geoms", [pieces]):
        if pc.is_empty or pc.area < 1e-6:
            continue
        rp = pc.representative_point()
        q = np.array([rp.x, rp.y])
        # side via the nearest divider segment
        d = np.hypot(*(P - q).T)
        i = int(np.clip(np.argmin(d), 0, len(P) - 2))
        a, b = P[i], P[i + 1]
        cr = (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
        # screen 'left' of travel has negative cross in y-down coordinates
        if (cr < 0) == (side > 0):
            keep.append(pc)
    return shapely.union_all(keep) if keep else shapely.Polygon()


def half(shape, divider, side: int = 1, angle: float = 45.0, spacing: float = 7.0, **kw) -> str:
    """Half-hatching (Monarchs/Drifters): hatch exactly one half of a shape
    split by ``divider`` (a line or curve — a leaf midrib, a pip axis),
    ``side`` +1 = left of the divider's direction on screen, -1 = right.
    Other keywords as :func:`parallel` (e.g. ``width=2.1, cap='butt'``).
    -> STROKE d (or FILL with ``width``)."""
    region = _region(shape, kw.pop("fill_rule", "nonzero"))
    if region.is_empty:
        return ""
    part = _side_pieces(region, divider, side)
    if part.is_empty:
        return ""
    return parallel(part, angle, spacing, **kw)


def contour(shape, spacing: float = 4.0, *, count: int | None = None, start: float | None = None,
            width: float | None = None, join: str = "round", fill_rule: str = "nonzero",
            min_area: float = 2.0) -> str:
    """Contour / offset hatching: concentric rings following the outline inward.
    ``start`` first inset (default spacing/2). -> STROKE d (closed rings) or FILL."""
    _positive("spacing", spacing)
    _choice("join", join, ("round", "miter", "bevel"))
    region = _region(shape, fill_rule)
    if region.is_empty:
        return ""
    st = spacing / 2 if start is None else start
    out = []
    k = 0
    while count is None or k < count:
        r = region.buffer(-(st + k * spacing), quad_segs=16,
                          join_style={"round": "round", "miter": "mitre", "bevel": "bevel"}[join])
        if r.is_empty or r.area < min_area:
            break
        polys = [r] if r.geom_type == "Polygon" else [p for p in getattr(r, "geoms", []) if p.geom_type == "Polygon"]
        for pg in polys:
            if pg.area < min_area:
                continue
            for ring in [pg.exterior, *pg.interiors]:
                c = np.asarray(ring.coords)
                out.append(c)
        k += 1
        if k > 2000:
            break
    if not out:
        return ""
    if width is None:
        return "".join(G.poly_d(c[:-1], True) for c in out)
    return G.outline([(c[:-1], True) for c in out], width)


def concentric(shape, center, spacing: float = 4.0, *, start: float = 0.0,
               width: float | None = None, taper: float = 0.0, ry_scale: float = 1.0,
               min_width: float = 0.0, fill_rule="nonzero") -> str:
    """Concentric circles (ellipses with ``ry_scale``) about ``center``, clipped."""
    _positive("spacing", spacing)
    _positive("ry_scale", ry_scale)
    region = _region(shape, fill_rule)
    if region.is_empty:
        return ""
    cx, cy = center
    x0, y0, x1, y1 = region.bounds
    rmax = max(math.hypot(px - cx, py - cy) for px in (x0, x1) for py in (y0, y1))
    lines = []
    r = start if start > 0 else spacing
    while r <= rmax / min(1.0, ry_scale) + spacing:
        n = max(24, int(2 * math.pi * r / 1.5))
        a = np.linspace(0, 2 * math.pi, n + 1)
        lines.append(np.column_stack([cx + r * np.cos(a), cy + r * ry_scale * np.sin(a)]))
        r += spacing
    return emit(_clip(lines, region), width, taper, min_width=min_width)


def radial(shape, center, n: int = 72, *, start_deg: float = 0.0, r0: float = 0.0,
           width: float | None = None, taper: float = 0.0, min_width: float = 0.0,
           fill_rule="nonzero") -> str:
    """Rays from ``center`` (every 360/n degrees), clipped to shape."""
    if n < 1:
        raise ValueError("radial: n must be >= 1")
    region = _region(shape, fill_rule)
    if region.is_empty:
        return ""
    cx, cy = center
    x0, y0, x1, y1 = region.bounds
    R = max(math.hypot(px - cx, py - cy) for px in (x0, x1) for py in (y0, y1)) + 1
    lines = []
    for k in range(n):
        a = math.radians(start_deg + 360.0 * k / n)
        u = np.array([math.cos(a), math.sin(a)])
        lines.append(np.array([np.array(center) + u * r0, np.array(center) + u * R]))
    return emit(_clip(lines, region), width, taper, min_width=min_width)


def along(shape, guide, spacing: float = 4.0, *, mode: str = "shift", count: int | None = None,
          both: bool = True, width: float | None = None, taper: float = 0.0,
          direction=None, extend: float = 2000.0, min_width: float = 0.0, fill_rule="nonzero") -> str:
    """Curved-flow hatch following ``guide``, clipped to shape.

    mode 'shift'  (default) translated copies of the guide stepped ``spacing`` apart
                  perpendicular to its chord (or along ``direction`` (dx,dy)) — the
                  classic engraved wave hatch; never cusps.
    mode 'offset' true parallel (offset) curves — follows bends exactly but tightens
                  on the concave side.
    The guide is extended tangentially so the family covers the shape.
    -> STROKE d or FILL (width)."""
    _positive("spacing", spacing)
    _choice("mode", mode, ("shift", "offset"))
    region = _region(shape, fill_rule)
    if region.is_empty:
        return ""
    cv = G.curve(guide)
    P = cv.resample(1.0)
    t0 = cv.tangent(0.0); t1 = cv.tangent(1.0)
    P = np.vstack([P[0] - t0 * extend, P, P[-1] + t1 * extend])
    x0, y0, x1, y1 = region.bounds
    reach = math.hypot(x1 - x0, y1 - y0) + math.hypot(*(cv.pts[-1] - cv.pts[0]))
    n = count if count is not None else int(reach / spacing) + 2
    ks = range(-n, n + 1) if both else range(0, n + 1)
    lines = []
    if mode == "shift":
        if direction is None:
            ch = cv.pts[-1] - cv.pts[0]
            ch = ch / max(np.hypot(*ch), 1e-9)
            dvec = np.array([ch[1], -ch[0]])
        else:
            dvec = np.asarray(direction, float)
            dvec = dvec / np.hypot(*dvec)
        for k in ks:
            lines.append(P + dvec * (k * spacing))
    else:
        base = LineString(P)
        for k in ks:
            oc = base if k == 0 else base.offset_curve(k * spacing, quad_segs=8, join_style="round")
            if oc.is_empty or not oc.intersects(region):
                continue
            lines += _lines_from_geom(oc)
    return emit(_clip(lines, region), width, taper, min_width=min_width)


def between(guide_a, guide_b, n: int = 12, *, clip=None, width: float | None = None,
            taper: float = 0.0, samples: int = 400, include_ends: bool = True,
            min_width: float = 0.0) -> str:
    """Interpolated flow lines morphing from ``guide_a`` to ``guide_b`` (both
    resampled by arc length) — the engraver's way of hatching a curved form.
    Optional ``clip`` shape. -> STROKE d or FILL (width)."""
    if n < 1:
        raise ValueError("between: n must be >= 1")
    A = G.curve(guide_a).sample(samples)
    B = G.curve(guide_b).sample(samples)
    if n == 1:
        ks = np.array([0.5])
    else:
        ks = np.linspace(0, 1, n) if include_ends else np.linspace(0, 1, n + 2)[1:-1]
    lines = [A * (1 - k) + B * k for k in ks]
    if clip is not None:
        reg = _region(clip)
        if reg.is_empty:
            return ""
        lines = _clip(lines, reg)
    return emit(lines, width, taper, min_width=min_width)


def latitudes(cx: float, cy: float, r: float, spacing: float = 5.0, *, tilt_deg: float = 25.0,
              rot_deg: float = 0.0, samples: int = 240) -> list[np.ndarray]:
    """Visible latitude lines of a sphere (orthographic, axis tilted toward viewer
    by ``tilt_deg``, rotated by ``rot_deg`` in the picture plane). Returns
    polylines (feed to :func:`engrave`); [] for r <= 0."""
    if not r > 0:
        return []
    _positive("spacing", spacing)
    tilt = math.radians(tilt_deg)
    out = []
    n = int(2 * r / spacing)
    for k in range(-n, n + 1):
        z = k * spacing / r  # latitude height in [-1,1]
        if abs(z) >= 1:
            continue
        rr = math.sqrt(1 - z * z)
        th = np.linspace(0, 2 * math.pi, samples)
        X = rr * np.cos(th)
        Y = z * np.ones_like(th)
        Z = rr * np.sin(th)
        Y2 = Y * math.cos(tilt) - Z * math.sin(tilt)
        Z2 = Y * math.sin(tilt) + Z * math.cos(tilt)
        vis = Z2 >= 0
        if not vis.any():
            continue
        idx = np.where(vis)[0]
        breaks = np.where(np.diff(idx) > 1)[0]
        runs = np.split(idx, breaks + 1)
        if len(runs) > 1 and runs[0][0] == 0 and runs[-1][-1] == samples - 1:
            runs = [np.r_[runs[-1], runs[0]]] + runs[1:-1]
        a = math.radians(rot_deg)
        for run in runs:
            if len(run) < 2:
                continue
            px = X[run] * r
            py = Y2[run] * r
            qx = cx + px * math.cos(a) - py * math.sin(a)
            qy = cy + px * math.sin(a) + py * math.cos(a)
            out.append(np.column_stack([qx, qy]))
    return out


def flow(shape, field: Callable, spacing: float = 5.0, *, step: float = 1.0,
         test_ratio: float = 0.55, min_len: float = 12.0, max_steps: int = 3000,
         seed_point=None, width: float | None = None, taper: float = 0.0,
         end_taper: float | None = None, singular=(), min_width: float = 0.0,
         fill_rule="nonzero") -> str:
    """Evenly-spaced streamlines (Jobard–Lefer) of a direction field, clipped.

    field(x, y) -> angle in radians, or a (dx, dy) tuple. Lines stay ``spacing``
    apart and stop at ``test_ratio*spacing`` from neighbours (or from
    themselves, so closed streamlines round a vortex terminate after one turn).
    Every part of the region is reached (each polygon, round holes): after the
    seed queue empties, a grid scan seeds any cell still empty.

    With ``width`` (FILL), ends that stop because they ran into a neighbour
    taper over ``end_taper`` px (default 3·spacing) instead of ending bluntly;
    ``taper`` fades every end (boundary ends too). Streamlines stay 1.5·spacing
    away from any point in ``singular`` and stop where the field turns more
    than 60° in one step (a singularity). -> STROKE d or FILL (width)."""
    _positive("spacing", spacing)
    _positive("step", step)
    region = _region(shape, fill_rule)
    if region.is_empty:
        return ""
    shapely.prepare(region)
    dsep = spacing
    dtest = spacing * test_ratio
    cell = dsep
    grid: dict[tuple, list] = {}
    sing = [np.asarray(p, float) for p in singular]
    sing_r2 = (1.5 * spacing) ** 2

    def direction(p):
        v = field(p[0], p[1])
        if np.ndim(v) == 0:
            v = float(v)
            if not math.isfinite(v):
                return None
            return np.array([math.cos(v), math.sin(v)])
        v = np.asarray(v, float).ravel()
        n = math.hypot(v[0], v[1])
        return v[:2] / n if n > 1e-12 and math.isfinite(n) else None

    def far_enough(p, dmin, own=None):
        gx, gy = int(p[0] // cell), int(p[1] // cell)
        rng = int(math.ceil(dmin / cell))
        d2 = (dmin * (1 - 1e-6)) ** 2
        for i in range(gx - rng, gx + rng + 1):
            for j in range(gy - rng, gy + rng + 1):
                for (q, lid) in grid.get((i, j), ()):
                    if own is not None and lid == own:
                        continue
                    if (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2 < d2:
                        return False
        return True

    def near_singular(p):
        return any((p[0] - s[0]) ** 2 + (p[1] - s[1]) ** 2 < sing_r2 for s in sing)

    def inside(p):
        return shapely.contains_xy(region, p[0], p[1])

    lag = 3.0 * dsep  # arc length before a line may be tested against itself

    def integrate(p0, lid):
        own: dict[tuple, list] = {}
        p0 = np.array(p0, float)
        own.setdefault((int(p0[0] // cell), int(p0[1] // cell)), []).append((p0, 0.0))

        def self_clear(q, sq):
            gx, gy = int(q[0] // cell), int(q[1] // cell)
            d2 = dtest * dtest
            for i in range(gx - 1, gx + 2):
                for j in range(gy - 1, gy + 2):
                    for (r, sr) in own.get((i, j), ()):
                        if abs(sq - sr) > lag and (r[0] - q[0]) ** 2 + (r[1] - q[1]) ** 2 < d2:
                            return False
            return True

        pts_f, pts_b = [], []
        why = {1: "edge", -1: "edge"}
        for sgn, acc in ((1, pts_f), (-1, pts_b)):
            p = p0.copy()
            prev_dir = None
            sp = 0.0
            for _ in range(max_steps):
                d1 = direction(p)
                if d1 is None:
                    why[sgn] = "singular"
                    break
                if prev_dir is not None and np.dot(d1, prev_dir) < 0:
                    d1 = -d1
                mid = p + sgn * d1 * step * 0.5
                d2 = direction(mid)
                if d2 is None:
                    why[sgn] = "singular"
                    break
                if np.dot(d2, d1) < 0:
                    d2 = -d2
                if prev_dir is not None and np.dot(d2, prev_dir) < 0.5:   # > 60° turn
                    why[sgn] = "singular"
                    break
                q = p + sgn * d2 * step
                sq = sp + sgn * step
                if not inside(q):
                    why[sgn] = "edge"
                    break
                if sing and near_singular(q):
                    why[sgn] = "singular"
                    break
                if not far_enough(q, dtest, own=lid):
                    why[sgn] = "near"
                    break
                if not self_clear(q, sq):
                    why[sgn] = "self"
                    break
                acc.append(q)
                own.setdefault((int(q[0] // cell), int(q[1] // cell)), []).append((q, sq))
                prev_dir = d2
                p, sp = q, sq
            if sgn == 1 and sp > 2 * lag and np.hypot(*(p - p0)) < 1.5 * dtest + step:
                return np.array([p0] + pts_f + [p0]), ("loop", "loop")
        pts = pts_b[::-1] + [p0] + pts_f
        return np.array(pts), (why[-1], why[1])

    def add_to_grid(line, lid):
        for q in line:
            grid.setdefault((int(q[0] // cell), int(q[1] // cell)), []).append((q, lid))

    lines, reasons = [], []
    lid = 0

    def grow(queue):
        nonlocal lid
        while queue:
            s = queue.pop(0)
            if not inside(s) or not far_enough(s, dsep) or (sing and near_singular(s)):
                continue
            line, why = integrate(s, lid)
            if len(line) < 2:
                continue
            L = np.hypot(*np.diff(line, axis=0).T).sum()
            if L < min_len:
                continue
            add_to_grid(line, lid)
            lines.append(line)
            reasons.append(why)
            stride = max(1, int(dsep / step))
            for k in range(0, len(line), stride):
                p = line[k]
                dvec = direction(p)
                if dvec is None:
                    continue
                nrm = np.array([-dvec[1], dvec[0]])
                # a hair beyond dsep so float error never rejects the candidate
                queue.append(p + nrm * dsep * 1.001)
                queue.append(p - nrm * dsep * 1.001)
            lid += 1
            if lid > 20000:
                return

    starts = []
    if seed_point is not None:
        starts.append(np.array(seed_point, float))
    parts = [region] if region.geom_type == "Polygon" else [g for g in getattr(region, "geoms", [])
                                                          if g.geom_type == "Polygon"]
    for pg in parts:
        rp = pg.representative_point()
        starts.append(np.array([rp.x, rp.y]))
    grow(starts)
    # grid-scan fallback: seed any part of the region the queue never reached
    x0, y0, x1, y1 = region.bounds
    for _ in range(3):
        gx = np.arange(x0 + dsep / 2, x1, dsep)
        gy = np.arange(y0 + dsep / 2, y1, dsep)
        X, Y = np.meshgrid(gx, gy)
        pts = np.column_stack([X.ravel(), Y.ravel()])
        pts = pts[shapely.contains_xy(region, pts[:, 0], pts[:, 1])]
        cand = [p for p in pts if far_enough(p, dsep) and not (sing and near_singular(p))]
        if not cand:
            break
        n0 = len(lines)
        for p in cand:
            if far_enough(p, dsep):
                grow([p])
        if len(lines) == n0:
            break
    if width is None:
        return emit(lines, None)
    et = 3 * spacing if end_taper is None else end_taper
    out = []
    for line, why in zip(lines, reasons):
        tl = taper
        ends = (bool(taper) or (why[0] == "near" and et > 0), bool(taper) or (why[1] == "near" and et > 0))
        if not any(ends):
            out.append(emit([line], width, 0.0, min_width=min_width))
            continue
        # per-end taper lengths: generic taper, or end_taper at 'near' ends
        cv = G.Curve(line)
        P = cv.resample(min(0.8, max(0.25, width)))
        s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
        Lr = s[-1]
        f = np.ones_like(s)
        for end, is_start in ((0, True), (1, False)):
            L_t = tl if tl else (et if why[end] == "near" else 0.0)
            if why[end] == "near":
                L_t = max(L_t, et)
            if L_t <= 0:
                continue
            L_t = min(L_t, Lr / 2)
            u = s / L_t if is_start else (Lr - s) / L_t
            f = f * ease(u)
        R = np.maximum(width / 2 * f, min_width / 2)
        out.append(variable_stroke(P, R))
    return "".join(out)


# =============================================================================
# tone functions (1 = darkest)
# =============================================================================
def clamp_tone(f: Callable) -> Callable:
    return lambda x, y: np.clip(f(x, y), 0.0, 1.0)


def _lambert(N, light, ambient):
    L = np.asarray(light, float)
    L = L / np.linalg.norm(L)
    lam = np.clip(N[0] * L[0] + N[1] * L[1] + N[2] * L[2], 0, 1)
    return 1 - (ambient + (1 - ambient) * lam)


def sphere_tone(cx: float, cy: float, r: float, light=(-0.55, -0.65, 0.52),
                ambient: float = 0.05, gamma: float = 1.0, rim: float = 0.0) -> Callable:
    """Lambert shading of a sphere: returns darkness in 0..1 (0 = highlight).
    ``rim`` adds a little reflected light at the shadow edge."""
    _positive("r", r)
    L = np.asarray(light, float)
    L = L / np.linalg.norm(L)

    def f(x, y):
        nx = (np.asarray(x, float) - cx) / r
        ny = (np.asarray(y, float) - cy) / r
        rr = nx * nx + ny * ny
        nz = np.sqrt(np.clip(1 - rr, 0, 1))
        lam = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
        dark = 1 - (ambient + (1 - ambient) * lam)
        if rim:
            dark = dark - rim * np.clip(rr, 0, 1) ** 4 * (lam <= 0.02)
        return np.clip(dark, 0, 1) ** gamma
    return f


def cylinder_tone(p0, p1, r: float, light=(-0.6, -0.5, 0.62), ambient: float = 0.05,
                  gamma: float = 1.0) -> Callable:
    """Lambert shading of a cylinder whose axis runs p0 -> p1 in the picture
    plane with radius ``r`` (columns, stems, rolled ribbon, sword blades)."""
    _positive("r", r)
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    ax = p1 - p0
    n = float(np.hypot(*ax))
    if n < 1e-9:
        raise ValueError("cylinder_tone: p0 and p1 coincide")
    ax = ax / n
    across = np.array([-ax[1], ax[0]])

    def f(x, y):
        dx = np.asarray(x, float) - p0[0]
        dy = np.asarray(y, float) - p0[1]
        u = np.clip((dx * across[0] + dy * across[1]) / r, -1, 1)
        nz = np.sqrt(1 - u * u)
        N = (across[0] * u, across[1] * u, nz)
        return np.clip(_lambert(N, light, ambient), 0, 1) ** gamma
    return f


def shape_distance_tone(shape, width: float = 10.0, t_edge: float = 1.0, t_inner: float = 0.0,
                        power: float = 1.5) -> Callable:
    """Tone by distance from a shape's edge: ``t_edge`` on the contour easing
    to ``t_inner`` ``width`` px inside (rounded, pillowed forms)."""
    _positive("width", width)
    region = _region(shape)
    bnd = region.boundary

    def f(x, y):
        x = np.asarray(x, float); y = np.asarray(y, float)
        d = shapely.distance(bnd, shapely.points(x.ravel(), y.ravel())).reshape(x.shape)
        u = np.clip(1 - d / width, 0, 1) ** power
        return t_inner + (t_edge - t_inner) * u
    return f


def bevel_tone(shape, light_angle: float = -135.0, width: float = 8.0, base: float = 0.15,
               strength: float = 0.85, power: float = 1.2) -> Callable:
    """Bevelled / embossed edge shading: within ``width`` px of the contour,
    edges whose outward normal faces away from the light (screen angle
    ``light_angle``, default from the top-left) darken; the lit edges stay at
    ``base``. Great for shields, cartouches, ribbons and pips."""
    _positive("width", width)
    region = _region(shape)
    bnd = region.boundary
    la = math.radians(light_angle)
    Ldir = np.array([math.cos(la), math.sin(la)])

    def f(x, y):
        x = np.asarray(x, float); y = np.asarray(y, float)
        pts = shapely.points(x.ravel(), y.ravel())
        sl = shapely.shortest_line(pts, bnd)
        co = shapely.get_coordinates(sl).reshape(-1, 2, 2)
        v = co[:, 1] - co[:, 0]
        d = np.hypot(v[:, 0], v[:, 1])
        nrm = v / np.maximum(d, 1e-9)[:, None]       # outward normal (inside points)
        facing = -(nrm @ Ldir)                       # >0: faces away from the light
        w = np.clip(1 - d / width, 0, 1) ** power
        t = base + strength * np.clip(facing, 0, 1) * w
        return t.reshape(x.shape)
    return f


def linear_tone(p0, p1, t0: float = 0.0, t1: float = 1.0) -> Callable:
    """Tone ramps from t0 at p0 to t1 at p1 (clamped)."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0
    L2 = float(d @ d)
    if L2 < 1e-12:
        raise ValueError("linear_tone: p0 and p1 coincide")

    def f(x, y):
        u = ((np.asarray(x, float) - p0[0]) * d[0] + (np.asarray(y, float) - p0[1]) * d[1]) / L2
        return t0 + (t1 - t0) * np.clip(u, 0, 1)
    return f


def radial_tone(center, r: float, t_center: float = 1.0, t_edge: float = 0.0,
                power: float = 1.0) -> Callable:
    _positive("r", r)
    cx, cy = center

    def f(x, y):
        u = np.clip(np.hypot(np.asarray(x, float) - cx, np.asarray(y, float) - cy) / r, 0, 1) ** power
        return t_center + (t_edge - t_center) * u
    return f


def _tone_eval(tone, x, y):
    if callable(tone):
        v = tone(x, y)
    else:
        v = tone
    return np.array(np.broadcast_to(np.asarray(v, float), np.shape(x)), float)


# =============================================================================
# tonal engraving
# =============================================================================
def engrave(lines, tone, *, wmin: float = 0.0, wmax: float = 2.4, gap: float = 0.9,
            clip=None, fade: float = 0.0, edge_gap: float = 0.0, spacing: float = 0.6,
            gamma: float = 1.0, smooth: int = 2, cap: str = "round",
            min_width: float | None = None, taper_len: float | None = None,
            stagger: float = 0.08, seed: int = 11) -> str:
    """Tonal engraving: each line's width swells with ``tone(x, y)`` (0..1,
    1 = dark; a callable or a constant): width = wmin + (wmax-wmin)*tone**gamma.

    * Where a line's width falls below its break threshold (``gap`` px, varied
      per line by ±``stagger`` of the width range so highlight edges dissolve
      instead of forming a hard iso-tone contour) the line breaks; each piece
      then tapers over ``taper_len`` px (default 3·wmax) down to ``min_width``
      (default: the offset-print minimum 1.05 px) and ends in a round cap.
    * ``clip``: lines are cut to the shape, inset by ``edge_gap`` px (a
      breathing gap before the contour); ``fade`` px eases widths toward the
      edge with a convex (u²) ramp.
    -> FILL d."""
    from . import tokens
    if isinstance(lines, str) or not (isinstance(lines, list) and lines and isinstance(lines[0], np.ndarray)):
        L = lines_of(lines)
    else:
        L = lines
    mw = tokens.MIN_LINE if min_width is None else float(min_width)
    tl = 3.0 * wmax if taper_len is None else float(taper_len)
    region = None
    if clip is not None:
        region = _region(clip)
        if edge_gap and not region.is_empty:
            region = region.buffer(-edge_gap)
        if region.is_empty:
            return ""
        L = _clip(L, region)
        bnd = region.boundary
    rng = np.random.default_rng(seed)
    out = []
    for l in L:
        cv = G.Curve(l)
        jit = rng.uniform(-1, 1)
        if cv.length < 0.5:
            continue
        P = cv.resample(spacing)
        t = np.clip(_tone_eval(tone, P[:, 0], P[:, 1]), 0, 1) ** gamma
        W = wmin + (wmax - wmin) * t
        if smooth and len(W) > 2 * smooth + 1:
            k = np.ones(2 * smooth + 1) / (2 * smooth + 1)
            W = np.convolve(np.pad(W, smooth, mode="edge"), k, mode="valid")
        if fade and region is not None:
            dist = shapely.distance(bnd, shapely.points(P[:, 0], P[:, 1]))
            W = W * np.clip(dist / fade, 0, 1) ** 2
        thr = max(1e-6, gap + stagger * (wmax - wmin) * jit)
        on = W >= thr
        if not on.any():
            continue
        s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
        idx = np.where(on)[0]
        runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        for run in runs:
            if len(run) < 2:
                continue
            a, b = run[0], run[-1]
            Pp = P[a:b + 1]
            Wp = W[a:b + 1].copy()
            sp = s[a:b + 1] - s[a]
            Lr = sp[-1]
            if Lr < 0.5:
                continue
            # length-based taper at ends that are tonal breaks (not line ends
            # at the clip boundary, which already fade)
            f = np.ones_like(sp)
            tlen = min(tl, Lr / 2)
            if a > 0 and tlen > 0:
                u = np.clip(sp / tlen, 0, 1)
                f = f * (u * u * (3 - 2 * u))
            if b < len(P) - 1 and tlen > 0:
                u = np.clip((Lr - sp) / tlen, 0, 1)
                f = f * (u * u * (3 - 2 * u))
            Wp = mw + (np.maximum(Wp, mw) - mw) * f
            out.append(variable_stroke(Pp, Wp / 2, start_cap="round", end_cap="round"))
    return "".join(out)


def tonal(shape, tone, *, angle: float = 45.0, spacing: float = 4.0,
          lines=None, wmin: float = 0.0, wmax: float | None = None, gap: float = 0.9,
          fade: float = 0.0, edge_gap: float = 0.0, gamma: float = 1.0,
          cross_at: float | None = None, cross_angle: float | None = None,
          min_width: float | None = None, taper_len: float | None = None,
          stagger: float = 0.08, seed: int = 11, fill_rule="nonzero") -> str:
    """Tonal engraving of a shape: parallel lines at ``angle`` (or supplied
    ``lines``) swelling with tone (see :func:`engrave` for gap, stagger,
    taper and edge options). ``cross_at``: where tone exceeds this value a
    second, finer cross-hatch layer is added at ``cross_angle`` (default
    angle+90) for deep shadows. -> FILL d."""
    _positive("spacing", spacing)
    region = _region(shape, fill_rule)
    if region.is_empty:
        return ""
    wmax = wmax if wmax is not None else spacing * 0.62
    base = lines if lines is not None else _clip(_parallel_lines(region, angle, spacing), region)
    kw = dict(gap=gap, clip=region, fade=fade, edge_gap=edge_gap, min_width=min_width,
              taper_len=taper_len, stagger=stagger)
    out = engrave(base, tone, wmin=wmin, wmax=wmax, gamma=gamma, seed=seed, **kw)
    if cross_at is not None:
        ca = cross_angle if cross_angle is not None else angle + 90
        t2 = lambda x, y: np.clip((_tone_eval(tone, x, y) - cross_at) / max(1e-6, 1 - cross_at), 0, 1)
        cl = _clip(_parallel_lines(region, ca, spacing), region)
        out += engrave(cl, t2, wmin=0, wmax=wmax * 0.8, seed=seed + 1, **kw)
    return out


# =============================================================================
# stipple & dot screens
# =============================================================================
def stipple(shape, tone, *, dmin: float = 2.2, dmax: float = 9.0, r: float = 0.75,
            r_tone: float = 0.0, seed: int = 7, k: int = 24, threshold: float = 0.02,
            fill_rule="nonzero") -> str:
    """Poisson-disk stipple: dot spacing goes from ``dmax`` (tone 0) to ``dmin``
    (tone 1); dots of radius ``r`` (+``r_tone``*tone). Areas with tone below
    ``threshold`` stay empty. Deterministic for a given ``seed``. -> FILL d."""
    _positive("dmin", dmin)
    _positive("dmax", dmax)
    _positive("r", r)
    region = _region(shape, fill_rule)
    if region.is_empty:
        return ""
    shapely.prepare(region)
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = region.bounds
    cell = dmin / math.sqrt(2)
    gw, gh = int((x1 - x0) / cell) + 2, int((y1 - y0) / cell) + 2
    grid = -np.ones((gw, gh), int)
    pts: list[np.ndarray] = []
    rads: list[float] = []
    rr_cells = int(math.ceil(dmax / cell))

    def spacing_at(P):
        t = np.clip(_tone_eval(tone, P[:, 0], P[:, 1]), 0, 1)
        return dmax + (dmin - dmax) * t

    def ok(p, rp):
        gx, gy = int((p[0] - x0) / cell), int((p[1] - y0) / cell)
        sub = grid[max(0, gx - rr_cells):gx + rr_cells + 1, max(0, gy - rr_cells):gy + rr_cells + 1]
        q = sub[sub >= 0]
        if not len(q):
            return True
        Q = np.asarray([pts[i] for i in q])
        need = 0.5 * (rp + np.asarray([rads[i] for i in q]))
        return bool(np.all((Q[:, 0] - p[0]) ** 2 + (Q[:, 1] - p[1]) ** 2 >= need * need))

    def add(p, rp):
        gx, gy = int((p[0] - x0) / cell), int((p[1] - y0) / cell)
        if grid[gx, gy] >= 0:
            return False
        grid[gx, gy] = len(pts)
        pts.append(p); rads.append(rp)
        return True

    # seed several starts so disconnected regions fill
    active = []
    S = np.column_stack([rng.uniform(x0, x1, 300), rng.uniform(y0, y1, 300)])
    S = S[shapely.contains_xy(region, S[:, 0], S[:, 1])]
    if len(S):
        for p, rp in zip(S, spacing_at(S)):
            if ok(p, rp) and add(p, rp):
                active.append(len(pts) - 1)
    while active:
        j = int(rng.integers(len(active)))
        i = active[j]
        base = pts[i]; rb = rads[i]
        ang = rng.uniform(0, 2 * math.pi, k)
        dist = rng.uniform(rb, 2 * rb, k)
        C = base + np.column_stack([np.cos(ang), np.sin(ang)]) * dist[:, None]
        inb = (C[:, 0] >= x0) & (C[:, 0] <= x1) & (C[:, 1] >= y0) & (C[:, 1] <= y1)
        C = C[inb]
        found = False
        if len(C):
            C = C[shapely.contains_xy(region, C[:, 0], C[:, 1])]
            if len(C):
                for p, rp in zip(C, spacing_at(C)):
                    if ok(p, rp) and add(p, rp):
                        active.append(len(pts) - 1)
                        found = True
                        break
        if not found:
            active[j] = active[-1]
            active.pop()
    if not pts:
        return ""
    P = np.array(pts)
    T = np.clip(_tone_eval(tone, P[:, 0], P[:, 1]), 0, 1)
    keep = T >= threshold
    out = []
    for (x, y), t in zip(P[keep], T[keep]):
        rr = r + r_tone * t
        out.append(G.circle_d(x, y, rr))
    return "".join(out)


def dot_screen(shape, spacing: float = 6.0, r: float = 1.0, *, tone=None,
               r_min: float = 0.0, angle: float = 0.0, grid: str = "hex", inset: float = 0.0,
               fade: float = 0.0, fill_rule="nonzero") -> str:
    """Regular dot field (Jinkens-style background texture / halftone).
    grid 'hex' | 'square'; radius r, or r_min..r modulated by ``tone``; dots are
    kept whole (only centres inside the shape inset by ``inset`` + radius);
    ``fade`` px shrinks dots toward the edge. -> FILL d."""
    _positive("spacing", spacing)
    _positive("r", r)
    _choice("grid", grid, ("hex", "square"))
    region = _region(shape, fill_rule)
    if region.is_empty:
        return ""
    inner = region.buffer(-(inset + r)) if (inset + r) > 0 else region
    if inner.is_empty:
        return ""
    x0, y0, x1, y1 = region.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + spacing
    dy = spacing * (math.sqrt(3) / 2 if grid == "hex" else 1.0)
    rows = int(R / dy) + 1
    cols = int(R / spacing) + 2
    J, I = np.meshgrid(np.arange(-rows, rows + 1), np.arange(-cols, cols + 1), indexing="ij")
    X = I * spacing + ((J % 2) * spacing / 2 if grid == "hex" else 0)
    Y = J * dy
    a = math.radians(angle)
    px = cx + X * math.cos(a) - Y * math.sin(a)
    py = cy + X * math.sin(a) + Y * math.cos(a)
    px, py = px.ravel(), py.ravel()
    m = shapely.contains_xy(inner, px, py)
    px, py = px[m], py[m]
    if tone is not None:
        rr = r_min + (r - r_min) * np.clip(_tone_eval(tone, px, py), 0, 1)
    else:
        rr = np.full(len(px), r)
    if fade:
        dist = shapely.distance(region.boundary, shapely.points(px, py))
        rr = rr * ease(dist / fade)
    keep = rr > 0.15
    return "".join(G.circle_d(x, y, q) for x, y, q in zip(px[keep], py[keep], rr[keep]))
