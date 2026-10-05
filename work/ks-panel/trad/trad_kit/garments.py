"""Garment pattern fills for court robes (all return Frags to hand to a
Scene Item as ``detail`` (line on ground) or ``knock`` (knocked out)).

    strata_fill(region, fault=((x0,y0),(x1,y1)))   §G.11 mantle bedding + jog
    karst_fill(region)                             §G.12 tunic voids
    inline(region, inset)                          parallel trim line inside an edge
    edge_band(outline, side_pts, width)            lining band along an edge
"""
from __future__ import annotations

import numpy as np
import shapely

from deck import tokens as T
from deck.motifs import core as MC
from deck.motifs import geometric as MG
from deck.motifs.core import Frag

from . import shapes as SH


def strata_fill(region, *, fault=None, y0=None, heights=(12.0, 19.0), jog=None, hatched="thin",
                color=T.INK, origin=None):
    return MG.strata(region, y0=y0, heights=heights, hatched=hatched, fault=fault, jog=jog,
                     color=color, origin=origin)


def karst_fill(region, *, pitch=(30.0, 23.0), sizes=(6.0, 10.0, 16.0), weights=(0.40, 0.35, 0.25),
               seed=1983, margin=None, origin=None, color=T.INK):
    return MG.karst_voids(region, pitch=pitch, sizes=sizes, weights=weights, seed=seed,
                          margin=margin, origin=origin, color=color)


def inline(region, inset: float, w: float = T.MEDIUM, *, keep=None, color=T.INK) -> Frag:
    """A line ``inset`` px inside the region's edge (a trim keyline). ``keep``
    (shapely) limits it to part of the region."""
    g = SH.shp(region).buffer(-inset, join_style=1, quad_segs=16)
    if keep is not None:
        pass
    lines = SH.boundary_lines(g)
    f = MC.stroke(lines, w, color=color) if lines else Frag()
    if keep is not None and f:
        f = MC.clip(f, keep)
    return f


def edge_band(poly, edge_pts, width: float, side: int = 1):
    """A band of ``width`` inside ``poly`` along the polyline ``edge_pts``
    (a stretch of its boundary): lining / trim region."""
    ls = shapely.LineString(edge_pts)
    band = ls.buffer(width, cap_style=2, join_style=1, single_sided=True) if side else ls.buffer(width)
    return band.intersection(SH.shp(poly))


def strata_bands(region, bands, *, fault=None, jog=12.0, y0=300.0, heights=(12.0, 19.0),
                 edge_w=T.FINE, color=T.INK):
    """§G.11 strata grouped into horizontal BANDS of courses (plain jade
    between them), with one diagonal fault: courses AND band edges on the
    fault's right-hand side (screen, looking p0→p1) drop by ``jog``. ``bands``
    = [(y_top, y_bottom), ...] on the course grid that starts at y0. The
    band edges are drawn as course lines so every hatch ends on a line."""
    reg = SH.shp(region)
    f = Frag()
    sides = [(reg, 0.0)]
    if fault is not None:
        L = MC.split_region(reg, fault, side=+1)
        R = MC.split_region(reg, fault, side=-1)
        sides = [(L, 0.0), (R, jog)]
    for part, dy in sides:
        if part.is_empty:
            continue
        for a, b in bands:
            win = part.intersection(shapely.box(0, a + dy, 750, b + dy))
            if win.is_empty:
                continue
            f += MG.strata(win, y0=y0 + dy, heights=heights, hatched="thin", color=color)
            for yy in (a + dy, b + dy):
                ln = shapely.LineString([(0, yy), (750, yy)]).intersection(part)
                segs = [p for p in SH.lines_of(ln) if len(p) >= 2]
                if segs:
                    f += MC.stroke(segs, edge_w, style="rule", color=color, role="course")
    if fault is not None:
        ln = shapely.LineString([fault[0], fault[1]]).intersection(reg)
        segs = [p for p in SH.lines_of(ln) if len(p) >= 2]
        if segs:
            f += MC.stroke(segs, T.MEDIUM, style="rule", color=color, role="fault")
    return f


def flooded_voids(region, *, min_d=15.0, **kw):
    """Karst voids (§G.12) whose largest cavities are water-filled.
    Returns (small_voids Frag, caverns shape, cavern_detail Frag): draw the
    small voids as line on the tunic; give the caverns a jade Item with FINE
    contours (outer = inner = FINE) and cavern_detail (the FINE ceiling
    offset) as its detail — the Edwards Aquifer: water in karst."""
    from inkkit import geom as G
    f = karst_fill(region, **kw)
    small, inner, big = Frag(), Frag(), []
    for m in f.marks:
        polys = G.flatten(m.d, 0.05)
        closed = [p for p, c in polys if c]
        if closed:
            g_ = shapely.Polygon(closed[0])
            x0, y0, x1, y1 = g_.bounds
            if (y1 - y0) >= min_d - 0.5:
                big.append(g_)
                continue
            small.marks.append(m)
        else:
            inner.marks.append(m)
    return small, (shapely.union_all(big) if big else shapely.Polygon()), inner
