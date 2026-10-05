"""art/_qs_garb.py — Q♠ · The Blind Oracle: garment patterns and trims.

Built the kit's way (deck.courtkit): FINE Aquifer patterns clipped to a
region's plain-bordered inside (§5 of COURT_GUIDE), knockouts as geometry,
every motif atomic (kept whole or dropped, never a stray arc).

    drops          §G.14 drips set as an all-over pattern: a half-drop grid of
                   single drips (a FINE stroke falling into a Ø6.3 terminal) —
                   the cave's slow water on the Oracle's mantle
    ripple_drops   a drip falling onto two ripple arcs (§G.8): the drop and
                   the rings it makes in the scrying pool
    drop_column    a column of knocked-out water drops (teardrops, point up)
                   down a red band: Drifters' lapel pips in the House of the Deep
    bordered       a region's plain border + FINE seam (the seam never runs
                   along the clipped bottom)
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C

P = K.P
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD


def bordered(reg, border, *, bottom=545.0, seam=True):
    """(inner region, seam Frag): ``reg`` inset by ``border`` everywhere except
    along its bottom edge (the band clip), closed by a FINE seam."""
    ext = reg.union(K.box(reg.bounds[0] + border + 2, bottom - 40, reg.bounds[2] - border - 2, bottom + 300))
    inner = ext.buffer(-border, quad_segs=16).intersection(K.box(0, 0, 2000, bottom + 20))
    inner = inner.intersection(reg)
    f = C.Frag()
    if seam:
        edge = inner.boundary.difference(K.box(0, bottom - 1, 2000, 3000))
        for ln in K._lines_of(edge):
            if ln.length > 6:
                f += K.line(C.polyline_d(np.asarray(ln.coords)), FINE, role="seam")
    return inner, f


def _grid(reg, pitch, origin):
    px, py = pitch
    x0, y0, x1, y1 = reg.bounds
    ox, oy = origin
    j0, j1 = int(math.floor((y0 - oy) / py)) - 1, int(math.ceil((y1 - oy) / py)) + 1
    for j in range(j0, j1 + 1):
        off = px / 2 if j % 2 else 0.0
        i0, i1 = int(math.floor((x0 - ox - off) / px)) - 1, int(math.ceil((x1 - ox - off) / px)) + 1
        for i in range(i0, i1 + 1):
            yield i, j, ox + off + i * px, oy + j * py


def drops(reg, *, pitch=(30.0, 30.0), origin=(375.0, 300.0), length=(9.0, 15.0), color=INK):
    """A half-drop grid of single drips: a FINE stroke falling ``length`` px
    into a Ø6.3 terminal (§G.14 drip, §I.14 terminal), lengths alternating
    row by row. Each drip is kept whole or dropped (its clear zone must lie
    inside ``reg``)."""
    f = C.Frag()
    safe = reg.buffer(-(K.GAP + K.TD / 2 + 0.2))
    for i, j, x, y in _grid(reg, pitch, origin):
        L = length[(i + j) % 2]
        top, tip = P(x, y - L / 2), P(x, y + L / 2)
        if not (safe.contains(Point(*top)) and safe.contains(Point(*tip))):
            continue
        d = C.stroke(C.polyline_d([top, tip]), FINE, color=color, role="drip") + C.dot(tip[0], tip[1], K.TD,
                                                                                         color=color, role="drip-t")
        f += K.atomic(d, f"drop{i}_{j}")
    return f


def ripple_drops(reg, *, pitch=(44.0, 40.0), origin=(375.0, 300.0), r=(7.0, 12.5), ry=0.42, drop=8.0,
                 color=INK):
    """A half-drop grid of 'drop and rings': a Ø6.3 drop above two ripple
    arcs (§G.8: the lower halves of concentric ellipses, radii ``r``, flattened
    ``ry``) — water falling into the cave pool."""
    f = C.Frag()
    safe = reg.buffer(-(K.GAP + FINE))
    for i, j, x, y in _grid(reg, pitch, origin):
        m = C.Frag()
        for rr in r:
            pts = [(x + rr * math.cos(t), y + rr * ry * math.sin(t)) for t in np.linspace(0.12, math.pi - 0.12, 40)]
            m += C.stroke(C.polyline_d(pts), FINE, color=color, role="ripple", terminals=None)
        dy = y - drop
        m += C.dot(x, dy, K.TD, color=color, role="drop")
        box = Point(x, y).buffer(r[-1] + 1.0).union(Point(x, dy).buffer(K.TD / 2 + 1))
        if not safe.contains(box.envelope.intersection(box.buffer(0))):
            continue
        f += K.atomic(m, f"rip{i}_{j}")
    return f


def teardrop(c, r, *, up=True, point=1.9):
    """A water drop: a circle of radius ``r`` drawn out to a point ``point`` × r
    above (``up``) or below its centre, the sides tangent to the circle. →
    region."""
    c = P(c)
    h = r * point
    tip = c + P(0.0, -h if up else h)
    a = math.degrees(math.acos(r / h))
    base = -90.0 if up else 90.0
    t0, t1 = P(*K.polar(c, r, base - a)), P(*K.polar(c, r, base + a))
    body = Point(*c).buffer(r, quad_segs=24)
    cone = Polygon([tuple(t0), tuple(tip), tuple(t1), tuple(c)])
    return body.union(cone)


def drop_column(band, path_pts, *, r=(2.6, 4.0), pitch=None, gap=3.0, up=True):
    """Knocked-out water drops (paper) down the centre line ``path_pts`` of a
    red ``band`` region, graduated from r[0] (top) to r[1] (bottom), each
    3 px clear of its neighbours and the band edge. → Frag of knockout
    shapes (strokes of width 0 are not used: fills) to subtract."""
    ln = LineString(path_pts)
    L = ln.length
    safe = band.buffer(-(MEDIUM / 2 + K.GAP_MARK))
    holes = []
    s = 0.0
    k = 0
    while s < L:
        t = s / L
        rr = r[0] + (r[1] - r[0]) * t
        p = ln.interpolate(s)
        dr = teardrop((p.x, p.y), rr, up=up)
        if safe.contains(dr):
            holes.append(dr)
        step = rr * (1.9 + 1.0) + gap
        s += step
        k += 1
    return K.U(*holes) if holes else Polygon()
