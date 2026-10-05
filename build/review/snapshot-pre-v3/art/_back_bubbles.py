"""Card back bubbles (brief §H.19 "bubble triads fill any leftover gaps, placed
C2"; §G.9 bubble beading).

A bubble triad is three bubbles on one line -- Ø 4.2 / 6.3 / 8.4 (the legal
dot sizes nearest the brief's 4 / 6 / 8), the small one a dot and the two
larger ones rings, so each reads as a bubble rising, smallest first.  The
triads are placed in the largest leftover pockets of flat jade: a pocket is
kept only where the triad can stand ``GAP`` (20 px) clear of every other
motif.  Every triad is placed with its 180° copy.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import Point
from shapely.ops import unary_union

from deck import tokens as T
from deck.motifs import core as C

from art import _back_geo as BG

FINE = T.FINE
CX, CY = T.CX, T.CY

SIZES = (4.2, 6.3, 8.4)


def triad(x, y, angle, sizes=SIZES, gap=4.2) -> C.Frag:
    """Three bubbles centred on (x, y) along screen ``angle`` (small ->
    large in the direction of rise)."""
    a = math.radians(angle)
    u = np.array([math.cos(a), math.sin(a)])
    styles = ["dot" if d < 6.0 else "ring" for d in sizes]
    outer = [d if st == "dot" else d + FINE for d, st in zip(sizes, styles)]
    L = sum(outer) + 2 * gap
    s = -L / 2
    f = C.Frag()
    for d, st, Do in zip(sizes, styles, outer):
        s += Do / 2
        p = np.array([x, y]) + u * s
        f += C.bubble(p[0], p[1], d, style=st)
        s += Do / 2 + gap
    return f


def column(p0, p1, d0=4.2, ratio=1.2, d_max=8.4, gap=5.0) -> C.Frag:
    """§G.9 bubble beading from p0 (bottom of the rise) toward p1."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.hypot(*(p1 - p0)))
    u = (p1 - p0) / L
    f = C.Frag()
    s, d, prev = 0.0, d0, None
    while True:
        st = "dot" if d < 6.0 else "ring"
        Do = d if st == "dot" else d + FINE
        if prev is not None:
            s += prev / 2 + gap + Do / 2
        if s > L:
            break
        p = p0 + u * s
        f += C.bubble(p[0], p[1], d, style=st)
        prev = Do
        d = min(d_max, d * ratio)
        if d0 >= d_max and prev == Do and s > L:
            break
    return f


def pockets(occupied, limit, clear, n=6, min_r=None):
    """Centres of the largest empty discs (radius >= ``min_r``) in ``limit``
    at least ``clear`` from ``occupied``, greedy, as (x, y, r)."""
    # (the motifs simplified by 0.25 px first: a 20 px buffer of every hatch line is slow)
    free = limit.difference(occupied.simplify(0.25).buffer(clear + 0.25, quad_segs=8))
    out = []
    for _ in range(n):
        if free.is_empty:
            break
        pts = []
        for g in getattr(free, "geoms", [free]):
            if g.area < 1.0:
                continue
            mic = shapely.maximum_inscribed_circle(g, 0.5)
            c = mic.coords[0]
            pts.append((mic.length, c))
        if not pts:
            break
        r, c = max(pts)
        if min_r is not None and r < min_r:
            break
        out.append((c[0], c[1], r))
        free = free.difference(Point(c).buffer(r + clear))
    return out
