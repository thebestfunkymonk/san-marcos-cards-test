"""Shared geometry for the card back emblem (brief §H.19).

Clock angles: 0 = 12 o'clock (toward the top lens tip), increasing
clockwise on screen, measured about the card centre (375, 525).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import box

from deck import tokens as T
from deck.motifs import core as C, geometric as M
from deck.motifs.forms import arc_spline, unit
from inkkit import geom as G

CX, CY = T.CX, T.CY
FINE, HAIR = T.FINE, T.HAIRLINE

GAP = 20.0                         # flat jade between distinct motifs (§H.19)
LENS_R, LENS_XC = 463.2, (181.8, 568.2)
LENS_IN = 6.3 + FINE / 2           # inner edge of the lens inner rule, inside the lens outline
WALL_GAP = 20.5                    # flat jade between the lens inner rule and the emblem
XLIM = 215.0                       # |x - 375| <= 215: the emblem spans <= 79.6 % of the lens width
ROSETTE_R = 130.0
R_IN = ROSETTE_R + FINE / 2 + GAP  # nothing of another motif nearer the centre than this


def pol(r, clock):
    """Point at radius r and clock angle (deg; 0 = 12 o'clock, clockwise)."""
    a = math.radians(clock)
    return (CX + r * math.sin(a), CY - r * math.cos(a))


def to_pol(p):
    dx, dy = p[0] - CX, p[1] - CY
    return math.hypot(dx, dy), math.degrees(math.atan2(dx, -dy)) % 360


def cw(clock):
    """Screen heading of the clockwise tangent at ``clock``."""
    return clock


def c2(f: C.Frag) -> C.Frag:
    """``f`` and its 180° copy.  The strokes are expanded to FILL outlines
    first, so both copies share one outline: stroking each copy separately
    can resolve a near-threshold miter (a sharp leaf point) differently in
    the rotated frame and break C2 by a 10 px spike."""
    f = f.to_fill()
    return f + f.rot180(CX, CY)


def lens_d():
    return M.lens_geometry(CX, 104.0, 946.0, 540.0)["d"]


def wall_r(clock, margin=WALL_GAP):
    """Distance from the centre to the inner edge of the lens inner rule
    along ``clock``, less ``margin``; also limited by XLIM."""
    a = math.radians(clock)
    sx, cy_ = math.sin(a), -math.cos(a)
    best = 1e9
    Rp = LENS_R - LENS_IN - margin
    for xc in LENS_XC:
        # |(CX - xc) + t sx, t cy|^2 = Rp^2
        b = (CX - xc) * sx
        cc = (CX - xc) ** 2 - Rp * Rp
        best = min(best, -b + math.sqrt(b * b - cc))
    if abs(sx) > 1e-9:
        best = min(best, XLIM / abs(sx))
    return best


def limit_region(margin=WALL_GAP):
    """Where the emblem may draw: the lens inset by LENS_IN + margin, and no
    wider than 2 x XLIM (the §H.19 70-80 % span)."""
    return C.region(G.offset(lens_d(), -(LENS_IN + margin))).intersection(
        box(CX - XLIM, 0, CX + XLIM, 2 * CY))


def pspline(rt, h0=None, h1=None, headings=None):
    """Smooth arc spline through polar stations [(r, clock), ...] (or plain
    (x, y) points when given as ('xy', x, y)).  Returns (d, dense pts)."""
    P = []
    for q in rt:
        if isinstance(q, tuple) and len(q) == 3 and q[0] == "xy":
            P.append((q[1], q[2]))
        elif isinstance(q, np.ndarray) or (isinstance(q, tuple) and len(q) == 2 and isinstance(q[0], np.ndarray)):
            P.append(tuple(q))
        else:
            P.append(pol(*q))
    d, pts, _ = arc_spline(P, h0, h1, headings=headings)
    return d, pts


def heading_at(pts, s=None, end=False):
    cv = G.Curve(np.asarray(pts, float))
    s = cv.length if end else (0.0 if s is None else s)
    t = cv.tangent_s(s)
    return math.degrees(math.atan2(t[1], t[0]))


def fillet(f: C.Frag, r: float = 1.5, role: str = "fillet") -> C.Frag:
    """Fill every sliver of jade narrower than 2r INSIDE the motif ``f`` (a
    morphological closing of its paper, r px): acute T-junction wedges, the
    points of converging contours, a hatch line grazing a corner.  Returns
    ``f`` plus the filled slivers as FILL marks, so the reversed-out motif
    keeps no jade finer than 2r (QA §I.12: HAIRLINE fills, 3 px bridges).
    Convex outlines and gaps wider than 2r are untouched."""
    sh = f.shape()
    if sh.is_empty:
        return f
    closed = sh.buffer(r, quad_segs=4, join_style="round").buffer(-r, quad_segs=4, join_style="round")
    extra = closed.difference(sh)
    # drop numerical dust along the stroke edges (buffer round-trips move them ~1e-3 px)
    extra = extra.buffer(-0.02).buffer(0.02)
    polys = [g for g in getattr(extra, "geoms", [extra]) if g.geom_type == "Polygon" and g.area > 0.05]
    if not polys:
        return f
    # overlap the motif slightly so the union with the strokes is seamless
    patch = shapely.union_all([g.buffer(0.05) for g in polys])
    g = f + C.fill(G.from_shape(patch), role=role)
    g._shape[(None, 0.0)] = shapely.union_all([sh, patch])     # seed the cache: the union is known
    return g
