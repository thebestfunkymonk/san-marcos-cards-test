"""art/_jc_hands.py — J♣ · The River Squire: the hand resting on the belt.

``belt_hand`` is ``courtkit.flat`` (the kit's hand laid flat, back to the
viewer) with the two refinements the resting pose needs at 3× — the same
treatment the Q♥'s bodice hand received, implemented locally because each
court owns its own helpers (kit-change candidate: ``flat(..., crease='web')``
and a smoothed ulnar edge):

* the THUMB's crease: the kit draws the thumb's lower outline where it lies
  over the back of the hand; with the thumb opened off the index finger (a
  clear web V between them) that outline is a short run meeting the web at a
  shallow angle, which heal trims to a floating dash. Here it is ONE MEDIUM
  crease that springs from the web's vertex and curves back toward the
  wrist along the thenar edge.
* the ULNAR EDGE (the little-finger side): the back-of-hand trapezoid and
  the little finger's capsule meet in a kink at the knuckle line; a local
  closing and a convex run over that step make that side one smooth edge.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K

P = K.P
MEDIUM = K.MEDIUM


def _local(at, angle):
    """Local → screen for a flat hand at ``at`` pointing ``angle``."""
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    o = P(at)

    def S(q):
        q = P(q)
        return o + P(c * q[0] - s * q[1], s * q[0] + c * q[1])
    return S


def belt_hand(at, angle, *, crease="web", crease_len=0.30, crease_sag=1.6, ulnar_r=5.0, radial_r=0.0, cuff=None,
              **kw) -> K.Hand:
    """``courtkit.flat(at, angle, **kw)`` with the web crease and a smooth
    ulnar edge (see the module docstring). ``crease_len``: × length;
    ``crease_sag``: px the crease bows toward the fingers. ``cuff`` =
    (region, (p0, p1)): the cuff the wrist goes into and its hand-side edge
    chord. The hand is cut exactly on the cuff's own (bowed) edge and
    everything on the arm side of that edge's chord goes: a wrist that meets
    the cuff at an angle (a hand bent down at the wrist) never shows a corner
    above or below the cuff, and the cuff edge is the one line at the
    junction (``Hand.add_to``'s own tuck is then skipped: ``stub`` 0). → Hand."""
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
        edge_zone = Polygon([tuple(S((0.0, -ts * (hw - 4.0)))), tuple(S((xk + 10.0, -ts * (hw - 4.0)))),
                             tuple(S((xk + 10.0, -ts * (hw + 8.0)))), tuple(S((0.0, -ts * (hw + 8.0))))])
        run = shape.intersection(Polygon([tuple(S((-2.0, -ts * (hw - 6.0)))), tuple(S((xk + 14.0, -ts * (hw - 6.0)))),
                                          tuple(S((xk + 14.0, -ts * (hw + 8.0)))),
                                          tuple(S((-2.0, -ts * (hw + 8.0))))]))
        shape = shape.union(closed.intersection(zone)).union(run.convex_hull.intersection(edge_zone))
        shape = max(K._polys_of(shape.buffer(0)), key=lambda g: g.area)

    # ---- the radial edge: the wrist rises into the thenar without a notch -----------------
    if radial_r:
        stub = float(kw.get("stub", 0.0))
        zone = Polygon([tuple(S((-stub - 2.0, 0.0))), tuple(S((L * 0.24, 0.0))),
                        tuple(S((L * 0.24, ts * (hw + 10.0)))), tuple(S((-stub - 2.0, ts * (hw + 10.0))))])
        closed = shape.buffer(radial_r, quad_segs=12).buffer(-radial_r, quad_segs=12)
        shape = max(K._polys_of(shape.union(closed.intersection(zone)).buffer(0)), key=lambda g: g.area)

    # ---- the thumb crease -----------------------------------------------------------------
    inner = hp.meta["inner"].select(lambda m: m.role != "thumb")
    if crease == "web":
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
                root = S((L * 0.14 + 4.0, ts * (min(float(kw.get("wrist_w", 24.0)), 0.78 * width) / 2 - 7.0)))
                u = root - V
                end = V + u / np.hypot(*u) * crease_len * L
                inner = inner + K.line(K.arc_sag(V, end, -ts * crease_sag), MEDIUM, role="thumb")
    if cuff is not None:
        creg, (c0, c1) = cuff
        c0, c1 = P(c0), P(c1)
        # the side of the edge line the fingers are on
        tip = S((L, 0.0))
        side = +1 if K.halfplane(c0, c1, side=+1).contains(Point(*tip)) else -1
        shape = shape.intersection(K.halfplane(c0, c1, side=side)).difference(K.R(creg))
        # drop the hairline spikes a cut along the bowed edge can leave
        shape = shape.buffer(-0.4, join_style=2, mitre_limit=4.0).buffer(0.4, join_style=2, mitre_limit=4.0)
        shape = max(K._polys_of(shape.buffer(0)), key=lambda g: g.area)
    lines = K.outline(shape) + inner
    part = K.Part(shape, hp.fills, lines, {**hp.meta, "inner": inner})
    return K.Hand(part, h.thumb, h.wrist, h.wrist_w, h.wrist_dir, 0.0 if cuff is not None else h.stub)
