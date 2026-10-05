"""§G.24 current lines — hair, beards, moustaches, plumes.

A *lock* is a ribbon region along a guide curve (filled gold, contoured) and
its *current lines*: 3–5 parallel offsets of the guide at a 7 px pitch.
Lines are clipped to the lock by the Scene, so where the lock tapers the
outer lines run into its contour (a butt join the contour covers, like
hatch); the free ends that remain carry Ø6.3 terminals, staggered so dots
never crowd a neighbour.

    g   = guide([(330, 222), (326, 260), (342, 300), (362, 334)])
    reg = lock_region(g, taper_width(20, 34, 6))
    ln  = current_lines(g, [-7, 0, 7], ends=[0.78, 0.92, 0.70])
"""
from __future__ import annotations

import math

import numpy as np

from deck import tokens as T
from deck.motifs import core as MC
from deck.motifs.core import Frag
from inkkit import geom as G

from . import shapes as SH

PITCH = T.HATCH_PITCH


def guide(pts) -> np.ndarray:
    return SH.spline(pts)


def lock_region(g, widths, *, cap0="flat", cap1="point"):
    if callable(widths):
        return SH.ribbon(g, 0, widths=widths, cap0=cap0, cap1=cap1)
    w0, w1 = widths
    return SH.ribbon(g, w0, w1, cap0=cap0, cap1=cap1)


def offset_line(g, off: float, t0: float = 0.0, t1: float = 1.0, *, converge: float = 0.0) -> np.ndarray:
    """The guide offset by ``off`` px along its left normal, between arc
    fractions t0..t1. ``converge`` (0..1) pulls the offset toward the guide
    as t -> 1 (strands gathering into a tip)."""
    cv = G.Curve(np.asarray(g, float))
    n = max(8, int(cv.length * (t1 - t0) / 0.75))
    t = np.linspace(t0, t1, n)
    k = 1.0 - converge * np.clip((t - 0.35) / 0.65, 0, 1) ** 1.5
    return cv.at(t) + cv.normal(t) * (off * k)[:, None]


def current_lines(g, offsets, *, starts=None, ends=None, converge: float = 0.0,
                  terminals=True, w: float = T.FINE, color: str = T.INK) -> Frag:
    """Parallel current lines along guide ``g``. ``ends[k]`` / ``starts[k]``
    are arc fractions where line k stops / starts; ``terminals`` (bool or a
    per-line list) puts a Ø6.3 terminal on each FREE end. Lines meant to run
    into a contour should extend past it (ends = 1.0 on a long guide) with
    terminals False — the Scene clips them onto the contour."""
    f = Frag()
    n = len(offsets)
    starts = starts or [0.0] * n
    ends = ends or [1.0] * n
    terms = terminals if isinstance(terminals, (list, tuple)) else [terminals] * n
    for off, a, b, t in zip(offsets, starts, ends, terms):
        P = offset_line(g, off, a, b, converge=converge)
        f += MC.stroke(P, w, color=color, role="current")
        if t:
            f += MC.terminal(*P[-1], color=color)
    return f


def lock_mass(outline_pts, ends, *, axis_side: int = -1):
    """A hair mass: a smooth outline (list of points, closed) whose lower edge
    is a row of rounded lock ends. ``ends`` = [(x0, x1, y_bottom), ...] from
    outside inward. Returns the shapely region."""
    import shapely
    from shapely.geometry import Polygon, Point
    body = Polygon(SH.spline(list(outline_pts) + [outline_pts[0]]))
    body = body if body.is_valid else shapely.make_valid(body)
    lobes = []
    for x0, x1, yb in ends:
        r = (x1 - x0) / 2
        lobes.append(Point((x0 + x1) / 2, yb - r).buffer(r, quad_segs=24))
        lobes.append(shapely.box(x0, yb - r - 14, x1, yb - r))
    g = shapely.union_all([body] + lobes)
    return g.buffer(3.0, quad_segs=12).buffer(-3.0, quad_segs=12)     # close notches


def strand(pts, *, terminal: bool = True, w: float = T.FINE, color: str = T.INK) -> Frag:
    """One free current line through pts, ending (last point) in a terminal."""
    P = SH.spline(pts)
    f = MC.stroke(P, w, color=color, role="current")
    if terminal:
        f += MC.terminal(*P[-1], color=color)
    return f


def curl(p, heading: float, r: float, turn: float = 270.0, *, cw: bool = True) -> np.ndarray:
    """A curl (spiral-ish arc of radius r, shrinking 35 %) starting at p with
    ``heading`` (screen degrees) — for curled lock ends."""
    t = MC.Turtle(p[0], p[1], heading)
    s = 1 if cw else -1
    steps = 6
    for i in range(steps):
        t.arc(r * (1 - 0.35 * i / steps), s * turn / steps)
    return MC.sample_d(t.d(), 0.5)[0][0]
