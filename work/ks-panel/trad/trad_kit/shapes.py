"""Path helpers for court construction (all final-size card px, y down)."""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from inkkit import geom as G

AXIS = 375.0
TOL = 0.05


# ---------------------------------------------------------------------------
# shapely <-> d
# ---------------------------------------------------------------------------
def shp(x):
    """d-string / point array / shapely -> valid shapely geometry."""
    if isinstance(x, shapely.Geometry):
        g = x
    elif isinstance(x, np.ndarray):
        g = Polygon(x)
    else:
        g = G.to_shape(x, tol=TOL)
    if not g.is_valid:
        g = shapely.make_valid(g)
    return g


def dstr(g) -> str:
    if isinstance(g, str):
        return g
    if g is None or g.is_empty:
        return ""
    return G.from_shape(g)


def polys(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    out = []
    for p in getattr(g, "geoms", []):
        out += polys(p)
    return out


def lines_of(g) -> list[np.ndarray]:
    """All LineString pieces of a geometry as point arrays."""
    if g is None or g.is_empty:
        return []
    t = g.geom_type
    if t == "LineString":
        return [np.asarray(g.coords)]
    if t == "LinearRing":
        return [np.asarray(g.coords)]
    out = []
    for p in getattr(g, "geoms", []):
        out += lines_of(p)
    return out


def boundary_lines(g) -> list[np.ndarray]:
    """Closed rings (exterior + holes) of every polygon, as point arrays."""
    out = []
    for p in polys(g):
        out.append(np.asarray(p.exterior.coords))
        out += [np.asarray(r.coords) for r in p.interiors]
    return out


# ---------------------------------------------------------------------------
# curves
# ---------------------------------------------------------------------------
def spline(pts, tension: float = 0.5) -> np.ndarray:
    """Dense Catmull-Rom polyline through pts (open)."""
    pts = np.asarray(pts, float)
    if len(pts) == 2:
        return seg(pts[0], pts[1])
    return G.spline(pts, closed=False, tension=tension, tol=0.02)


def seg(p0, p1, step: float = 1.0) -> np.ndarray:
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    n = max(2, int(math.ceil(np.hypot(*(p1 - p0)) / step)) + 1)
    t = np.linspace(0, 1, n)[:, None]
    return p0 + (p1 - p0) * t


def arc(cx, cy, r, a0, a1, ry=None, n=None) -> np.ndarray:
    """Points on a circular/elliptic arc a0 -> a1 (screen degrees)."""
    ry = r if ry is None else ry
    if n is None:
        n = max(8, int(abs(a1 - a0) / 2) + 2)
    a = np.radians(np.linspace(a0, a1, n))
    return np.column_stack([cx + r * np.cos(a), cy + ry * np.sin(a)])


def runs(*parts, closed: bool = True) -> np.ndarray:
    """Concatenate runs into one polyline. Each part is ('s', pts) for a smooth
    Catmull-Rom run, ('l', pts) for straight segments, or ('p', dense) for a
    ready polyline. Consecutive runs should share their joint point, which
    becomes a corner."""
    out = []
    for kind, pts in parts:
        pts = np.asarray(pts, float)
        if kind == "s":
            d = spline(pts)
        elif kind == "l":
            d = np.vstack([seg(a, b) for a, b in zip(pts[:-1], pts[1:])])
        else:
            d = pts
        if out and np.hypot(*(out[-1][-1] - d[0])) < 1e-6:
            d = d[1:]
        out.append(d)
    P = np.vstack(out)
    if closed and np.hypot(*(P[0] - P[-1])) < 1e-6:
        P = P[:-1]
    return P


def mirror_pts(P, axis: float = AXIS) -> np.ndarray:
    P = np.asarray(P, float).copy()
    P[:, 0] = 2 * axis - P[:, 0]
    return P


def bilateral_poly(left, axis: float = AXIS) -> Polygon:
    """Closed symmetric outline from its LEFT half: ``left`` runs from a point
    on the axis (top) down the left side to a point on the axis (bottom).
    Returns the polygon of left + mirrored(right)."""
    L = np.asarray(left, float)
    R = mirror_pts(L[::-1], axis)
    ring = np.vstack([L, R[1:-1]])
    g = Polygon(ring)
    return g if g.is_valid else shapely.make_valid(g)


def mirror_geom(g, axis: float = AXIS):
    return shapely.affinity.scale(g, xfact=-1, yfact=1, origin=(axis, 0))


def with_mirror(g, axis: float = AXIS):
    return shapely.union_all([g, mirror_geom(g, axis)])


def ribbon(guide, w0: float, w1: float | None = None, *, cap0: str = "flat", cap1: str = "round",
           widths=None, step: float = 0.75) -> Polygon:
    """A ribbon (lock / band) of width w0 -> w1 along a guide polyline.
    ``widths`` may be a callable t -> width. cap 'round' | 'point' | 'flat'."""
    cv = G.Curve(np.asarray(guide, float))
    n = max(3, int(cv.length / step))
    t = np.linspace(0, 1, n)
    if widths is None:
        w1 = w0 if w1 is None else w1
        W = w0 + (w1 - w0) * t
    else:
        W = np.array([widths(x) for x in t])
    P = cv.at(t)
    N = cv.normal(t)
    L = P + N * (W[:, None] / 2)
    R = P - N * (W[:, None] / 2)
    pieces = [L, R[::-1]]
    ring = np.vstack(pieces)
    g = Polygon(ring)
    if not g.is_valid:
        g = shapely.make_valid(g).buffer(0)
    if cap1 == "round":
        g = g.union(shapely.Point(*P[-1]).buffer(W[-1] / 2, quad_segs=24))
    elif cap1 == "point":
        tip = P[-1] + cv.tangent(1.0) * W[-1] * 0.9
        g = g.union(Polygon([L[-1], tip, R[-1]]))
    if cap0 == "round":
        g = g.union(shapely.Point(*P[0]).buffer(W[0] / 2, quad_segs=24))
    return g


def taper_width(w_root: float, w_mid: float, w_tip: float, mid: float = 0.45):
    """t -> width: swells from root to mid then tapers to the tip (lock profile)."""
    def f(t):
        if t <= mid:
            u = t / mid
            return w_root + (w_mid - w_root) * math.sin(u * math.pi / 2)
        u = (t - mid) / (1 - mid)
        return w_mid + (w_tip - w_mid) * (1 - math.cos(u * math.pi / 2))
    return f


def smooth_poly(g, r: float):
    """Round the corners of a polygon by open/close with radius r."""
    return g.buffer(r, quad_segs=16).buffer(-2 * r, quad_segs=16).buffer(r, quad_segs=16)
