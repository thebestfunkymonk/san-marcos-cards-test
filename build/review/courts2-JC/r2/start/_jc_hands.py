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
import shapely
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


# =============================================================================
# round 2: the forearm, its cuff and the hand as one arm
# =============================================================================
def _u(v):
    v = P(v)
    return v / float(np.hypot(*v))


def forearm(elbow, wrist, *, r_elbow=23.0, w_wrist=32.0, cuff_depth=12.0, into=2.5):
    """The viewer's-left forearm as one tapered capsule: a round elbow
    (``r_elbow`` about ``elbow``) and the cuff's top chord ``w_wrist`` wide,
    ``cuff_depth`` behind the wrist point ``wrist`` (the cuff's hand-side
    edge centre), square to the forearm axis. → (region, (p0, p1)) — the
    cuff's top chord in the order ``_jc_body.cuff`` wants (its depth runs
    toward the hand)."""
    E, W = P(elbow), P(wrist)
    u = _u(W - E)
    d = P(-u[1], u[0])
    c = W - u * cuff_depth
    p0, p1 = c - d * w_wrist / 2.0, c + d * w_wrist / 2.0
    end = Polygon([tuple(p0), tuple(p1), tuple(p1 + u * into), tuple(p0 + u * into)])
    reg = K.circle(E, r_elbow)
    reg = K.R(reg).union(end).convex_hull
    return reg, (p0, p1)


def rest_hand(wrist, angle, *, fore, cuff=None, lead=6.0, sweep_r=6.0, hide=None, crease="web", crease_len=0.30,
              crease_sag=1.6, ulnar_r=5.0, radial_r=0.0, **kw) -> K.Hand:
    """A hand laid on the belt (``courtkit.flat`` via ``belt_hand``) whose
    wrist comes out of the cuff ALONG the forearm and then turns: the flat
    hand is built ``lead`` px out along the forearm direction ``fore`` (unit,
    elbow → wrist) from the cuff's edge centre ``wrist``, pointing ``angle``,
    and a tapered sweep (the hull of the wrist's section in the cuff and the
    back of the hand's first fifth) joins them, the inside of the bend
    closed on a round of ``sweep_r``. ``hide`` = a region in FRONT of the
    thumb (the belt the thumb is hooked behind): the thumb's part inside it
    is removed, so the belt's own edge crosses it. Other kw → ``belt_hand``."""
    W = P(wrist)
    u = _u(fore)
    n = P(-u[1], u[0])
    H = W + u * lead
    kw = dict(kw)
    kw["stub"] = 0.0
    L = float(kw.get("length", 56.0))
    width = float(kw.get("width", 30.0))
    ww = min(float(kw.get("wrist_w", 24.0)), float(kw.get("taper", 0.78)) * width) / 2.0
    h = belt_hand(H, angle, crease=crease, crease_len=crease_len, crease_sag=crease_sag, ulnar_r=ulnar_r,
                  radial_r=radial_r, cuff=None, **kw)
    shape = h.hand.shape
    S = _local(H, angle)
    # the back of the hand's first fifth (its section just past the wrist)
    first = shape.intersection(Polygon([tuple(S((-1.0, -width))), tuple(S((0.20 * L, -width))),
                                        tuple(S((0.20 * L, width))), tuple(S((-1.0, width)))]))
    sec = Polygon([tuple(W - u * 4.0 + n * ww), tuple(W - u * 4.0 - n * ww), tuple(W + u * 0.5 - n * ww),
                   tuple(W + u * 0.5 + n * ww)])
    sweep = shapely.union_all([first, sec]).convex_hull
    full = shape.union(sweep)
    zone = sweep.buffer(sweep_r + 2.0)
    closed = full.buffer(sweep_r, quad_segs=12).buffer(-sweep_r, quad_segs=12)
    full = full.union(closed.intersection(zone))
    full = max(K._polys_of(full.buffer(0)), key=lambda g: g.area)
    inner = h.hand.meta["inner"]
    if hide is not None:
        # the thumb hooked behind ``hide``: the part of it inside goes (the body of the
        # hand — the same flat hand with a vestigial thumb — stays whole)
        kb = dict(kw)
        kb["thumb_len"] = 0.05
        body = K.flat(H, angle, **kb).hand.shape.union(sweep).buffer(0.3)
        gone = full.intersection(K.R(hide)).difference(body)
        if gone.area > 1.0:
            full = max(K._polys_of(full.difference(gone).buffer(0)), key=lambda g: g.area)
            inner = K.clip_out(inner, K.R(hide).difference(body.buffer(-0.5)), eps=0.0, trap=0.0)
    if cuff is not None:
        creg, (c0, c1) = cuff
        c0, c1 = P(c0), P(c1)
        tip = S((L, 0.0))
        side = +1 if K.halfplane(c0, c1, side=+1).contains(Point(*tip)) else -1
        full = full.intersection(K.halfplane(c0, c1, side=side)).difference(K.R(creg))
        full = full.buffer(-0.4, join_style=2, mitre_limit=4.0).buffer(0.4, join_style=2, mitre_limit=4.0)
        full = max(K._polys_of(full.buffer(0)), key=lambda g: g.area)
    lines = K.outline(full) + inner
    part = K.Part(full, h.hand.fills, lines, {**h.hand.meta, "inner": inner})
    return K.Hand(part, h.thumb, W, h.wrist_w, -u, 0.0)
