"""Shared geometry for the card back emblem (brief §H.19).

Clock angles: 0 = 12 o'clock (toward the top lens tip), increasing
clockwise on screen, measured about the card centre (375, 525).
"""
from __future__ import annotations

import math

import numpy as np
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
WALL_GAP = 22.0                    # flat jade between the lens inner rule and the emblem
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
