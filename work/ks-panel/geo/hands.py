"""Court hands (§H.0): mitten shapes, 3 finger lines and a separate thumb,
closed around cylindrical attributes. Compass construction.

    fist_on_shaft(x, y, ...)      a fist closed round a vertical shaft
    hand_under_sphere(c, r, ...)  a hand holding a sphere from below

Each returns (hand Part, thumb Part): add the attribute, then the hand, then
the thumb to a Scene, so the thumb lies over the fingers and the fingers over
the attribute.
"""
from __future__ import annotations

import math

import numpy as np
import shapely

import kit as K
from deck.motifs import core as C
from hair import Part


def _capsule(p0, p1, r):
    """Stadium (two semicircles + two tangents) from p0 to p1, radius r."""
    return shapely.LineString([tuple(p0), tuple(p1)]).buffer(r, quad_segs=24)


def fist_on_shaft(x, y, *, w=36.0, h=34.0, back=+1, wrist=(563.0, 454.0), wrist_w=25.0,
                  thumb_len=26.0, thumb_r=6.4):
    """Fist gripping a vertical shaft at (x, y). The four curled fingers cross
    the shaft toward the viewer: a block ``w`` × ``h`` whose fingertip side
    (away from ``back``) is a semicircle of radius h/2 struck on the block's
    mid-line — so the three finger lines (MEDIUM, horizontal) end on a true
    circle. The back of the hand runs from the block to ``wrist``. The thumb
    is a stadium lying over the index finger, pointing toward the fingertips."""
    sg = back
    y0, y1 = y - h / 2, y + h / 2
    x_tip = x - sg * w / 2               # fingertip extreme
    xc = x_tip + sg * h / 2              # centre of the fingertip semicircle
    x_back = x + sg * w / 2
    block = K.box(min(xc, x_back), y0, max(xc, x_back), y1).union(
        shapely.Point(xc, y).buffer(h / 2, quad_segs=32))
    W = K.P(wrist)
    u = W - K.P(x_back - sg * 8, y)
    u = u / np.hypot(*u)
    n = np.array([u[1], -u[0]])
    palm = shapely.Polygon([(x_back - sg * 14, y0 + 4), (x_back, y0 + 8), (x_back, y1 - 6),
                            tuple(W + n * wrist_w / 2), tuple(W - n * wrist_w / 2),
                            (x_back - sg * 16, y1)]).convex_hull
    hand = block.union(palm)
    lines = K.outline(K.D(hand))
    pitch = h / 4
    for k in (1, 2, 3):
        yy = y0 + k * pitch
        dy = yy - y
        xt = xc - sg * math.sqrt(max((h / 2) ** 2 - dy ** 2, 0))     # on the fingertip circle
        xe = x + sg * (w * 0.18)
        lines += K.line(f"M{xt} {yy}L{xe} {yy}", K.MEDIUM)
    # thumb over the index finger: from the back of the hand toward the tips
    t_root = K.P(x_back - sg * 3, y0 + 6)
    t_tip = K.P(x_back - sg * thumb_len, y0 + 1.5)
    thumb = _capsule(t_root, t_tip, thumb_r)
    th = Part(thumb, C.Frag(), K.outline(K.D(thumb)), {})
    return Part(hand, C.Frag(), lines, {"tip_x": x_tip}), th


def hand_under_sphere(c, r, *, wrist=(276.0, 462.0), wrist_w=24.0, span=(-12.0, 212.0), thick=12.0,
                      thumb_at=150.0, fingers=(8.0, 26.0, 44.0), wrist_at=118.0):
    """A hand holding a sphere (c, r) from below — ONE annular sector
    concentric with the sphere (inner arc = the sphere's own circle, outer
    arc r + ``thick``) from ``span[0]`` (the fingertips, on the right) round
    the bottom to ``span[1]`` (the thumb tip, up the left side), both ends
    round. Radial MEDIUM lines: three finger lines at ``fingers`` (degrees)
    and the thumb joint at ``thumb_at``. The wrist leaves the sector's outer
    arc around ``wrist_at`` for ``wrist`` (a trapezoid).
    Returns (hand Part, empty thumb Part) — the thumb is part of the sector."""
    c = K.P(c)
    a0, a1 = span
    ro = r + thick
    mid = r + thick / 2
    ang = np.radians(np.linspace(a0, a1, 241))
    inner = np.column_stack([c[0] + r * np.cos(ang), c[1] + r * np.sin(ang)])
    outer = np.column_stack([c[0] + ro * np.cos(ang), c[1] + ro * np.sin(ang)])
    sector = shapely.Polygon(np.vstack([inner, outer[::-1]]))
    for a in (a0, a1):
        sector = sector.union(shapely.Point(*K.polar(c, mid, a)).buffer(thick / 2, quad_segs=24))
    # the thumb tip is slimmer: taper by cutting with a circle struck inside
    W = K.P(wrist)
    wa, wb = K.polar(c, ro - 3, wrist_at - 16), K.polar(c, ro - 3, wrist_at + 16)
    u = W - (wa + wb) / 2
    u = u / np.hypot(*u)
    n = np.array([u[1], -u[0]])
    wristq = shapely.Polygon([tuple(wa), tuple(wb), tuple(W + n * wrist_w / 2), tuple(W - n * wrist_w / 2)]).convex_hull
    hand = sector.union(wristq).difference(shapely.Point(*c).buffer(r - 0.01, quad_segs=48))
    lines = K.outline(K.D(hand))
    for a in fingers:
        pa, pb = K.polar(c, r, a), K.polar(c, ro, a)
        lines += K.line(f"M{pa[0]} {pa[1]}L{pb[0]} {pb[1]}", K.MEDIUM)
    pa, pb = K.polar(c, r, thumb_at), K.polar(c, ro, thumb_at)
    lines += K.line(f"M{pa[0]} {pa[1]}L{pb[0]} {pb[1]}", K.MEDIUM)
    return Part(hand, C.Frag(), lines, {}), Part(shapely.Polygon(), C.Frag(), C.Frag(), {})
