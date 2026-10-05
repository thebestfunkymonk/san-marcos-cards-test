"""art/_qh_hand.py — the Q♥ hand laid on the bodice (§H.0 mitten, §H.5).

The court-local ``lady_hand`` this module used to hold was replaced by the
kit's ``courtkit.flat`` (courts2 kit review). ``bodice_hand`` is a thin
wrapper round that call that fixes two things the Q♥ pose shows at 3× and
that a queen's hand on her breast cannot carry:

* the THUMB's crease: the kit draws the thumb's lower outline where it lies
  over the back of the hand. With the thumb opened off the index finger (so
  the web shows as a clear V instead of the thumb's tip pressing the index
  root) that outline is a short run meeting the web at a shallow angle, which
  heal trims to a floating dash. Here it is replaced by ONE MEDIUM crease that
  springs from the web's vertex (touching the silhouette, so there is no
  near-miss) and curves back toward the wrist along the thenar edge, ending
  clear of every other line — or dropped (``crease=None``).
* the ULNAR EDGE (the little-finger side): the kit's back-of-hand trapezoid
  and the little finger's capsule meet in a small kink at the knuckle line;
  a local closing (``ulnar_r``) and the convex run over that step make that
  side one smooth edge from the wrist to the little fingertip.

Kit-change candidate: ``courtkit.flat(..., crease='web')`` and a smoothed
ulnar edge (reported, not implemented in the kit: other courts own it).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C

P = K.P
MEDIUM = K.MEDIUM


def _local(M_at, angle):
    """Local → screen for a flat hand at ``M_at`` pointing ``angle``."""
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    o = P(M_at)

    def S(q):
        q = P(q)
        return o + P(c * q[0] - s * q[1], s * q[0] + c * q[1])
    return S


def bodice_hand(at, angle, *, crease="web", crease_len=0.30, crease_sag=1.6, ulnar_r=5.0, **kw) -> K.Hand:
    """``courtkit.flat(at, angle, **kw)`` with the web crease and a smooth
    ulnar edge (see the module docstring). ``crease_len``: × length;
    ``crease_sag``: px the crease bows toward the fingers. → Hand."""
    h = K.flat(at, angle, **kw)
    hp = h.hand
    L = float(kw.get("length", 56.0))
    width = float(kw.get("width", 30.0))
    side = kw.get("side", -1)
    ts = -1.0 if side < 0 else 1.0
    xk = L * float(kw.get("knuckle", 0.50))
    hw = width / 2.0
    S = _local(at, angle)
    shape = hp.shape

    # ---- the ulnar edge: one smooth run from the wrist to the little finger -------------
    if ulnar_r:
        stub = float(kw.get("stub", 0.0))
        zone = Polygon([tuple(S((-stub - 2.0, 0.0))), tuple(S((xk + 6.0, 0.0))),
                        tuple(S((xk + 6.0, -ts * (hw + 8.0)))), tuple(S((-stub - 2.0, -ts * (hw + 8.0))))])
        closed = shape.buffer(ulnar_r, quad_segs=12).buffer(-ulnar_r, quad_segs=12)
        # a flat step where the little finger's column leaves the back: run the
        # edge on straight over it (the convex run, only along that side)
        edge_zone = Polygon([tuple(S((0.0, -ts * (hw - 4.0)))), tuple(S((xk + 10.0, -ts * (hw - 4.0)))),
                             tuple(S((xk + 10.0, -ts * (hw + 8.0)))), tuple(S((0.0, -ts * (hw + 8.0))))])
        run = shape.intersection(Polygon([tuple(S((-2.0, -ts * (hw - 6.0)))), tuple(S((xk + 14.0, -ts * (hw - 6.0)))),
                                          tuple(S((xk + 14.0, -ts * (hw + 8.0)))), tuple(S((-2.0, -ts * (hw + 8.0))))]))
        shape = shape.union(closed.intersection(zone)).union(run.convex_hull.intersection(edge_zone))
        shape = max(K._polys_of(shape.buffer(0)), key=lambda g: g.area)

    # ---- the thumb crease -----------------------------------------------------------------
    inner = hp.meta["inner"].select(lambda m: m.role != "thumb")
    if crease == "web":
        # the web's vertex: the deepest point of the pocket between the thumb and the index
        hull = shape.convex_hull
        guess = Point(*S((xk * 0.95, ts * hw)))
        pockets = [g for g in K._polys_of(hull.difference(shape.buffer(0.01))) if g.area > 4.0]
        if pockets:
            pk = min(pockets, key=lambda g: g.distance(guess))
            ring = LineString(np.asarray(shape.exterior.coords))
            seg_ = ring.intersection(pk.buffer(0.05))
            best, bd = None, -1.0
            for ln in K._lines_of(seg_):
                for q in np.asarray(ln.coords):
                    d = hull.exterior.distance(Point(*q))
                    if d > bd:
                        best, bd = P(q), d
            if best is not None:
                V = best
                # back toward the wrist along the thenar edge: aim at the thumb's root
                root = S((L * 0.14 + 4.0, ts * (min(float(kw.get("wrist_w", 24.0)), 0.78 * width) / 2 - 7.0)))
                u = root - V
                Lc = crease_len * L
                end = V + u / np.hypot(*u) * Lc
                d = K.arc_sag(V, end, -ts * crease_sag)
                inner = inner + K.line(d, MEDIUM, role="thumb")
    lines = K.outline(shape) + inner
    part = K.Part(shape, hp.fills, lines, {**hp.meta, "inner": inner})
    return K.Hand(part, h.thumb, h.wrist, h.wrist_w, h.wrist_dir, h.stub)
