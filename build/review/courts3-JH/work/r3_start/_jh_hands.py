"""art/_jh_hands.py — the J♥ minstrel's hands, seated on the kit fists.

Local helpers for art/JH.py only (deck/courtkit.py is shared; nothing here
changes it). Both hands are kit fists (§H.0 mitten, 3 finger lines, thumb over
the top); what this module adds is where and how they meet the arm and the
held object:

* ``fiddle_arm`` — the figure's LEFT forearm under the fiddle hand: a kit
  sleeve (jade forearm, Gill Red cuff — the same arm as the bow hand's)
  leaning 20° (the elbow down and in, behind the body), whose forearm is
  kept only where the fiddle body hides it. What shows is the red cuff: its
  inner end runs in under the neck, its own lower edge lies well behind the
  upper bout and its outer side crosses the bout at a clear angle — never a
  cuff edge lying along the bout.
* ``seat_on_neck`` — stacks the fiddle fist cut on that cuff's edge (0.6 px
  inside it: an exact cut leaves zero-width slits in the silhouette union)
  with its HEEL run on to the neck's edge (the palm's heel pressed against
  the neck). The kit keeps a heel 7.3 px off a shaft, which beside a
  CONTOUR-edged neck leaves a 1 px paper slot between two CONTOURs that
  prints as an ink block; here the pocket between heel, neck and cuff is
  hand. The back of the hand is closed over the kink where the kit's
  knuckle round meets the wrist's sweep.
* ``smooth_back`` — the same closing on the bow hand's back (knuckle side
  only).
* ``heel_paper`` — the bow hand: the kit turns the ground between a heel and
  a haloed shaft to paper, but not where that ground is an item named like an
  arm (the puff ``sleeveL`` behind the bow hand), which left a 3 px jade
  sliver between the heel's contour and the frog's paper channel; this adds
  the same paper channel for it (also for the 3 px jade dot between the
  stick's channel and the top of the fist).

The kit's thumb/index construction is kept as drawn on every court (one
hand language): on the narrow fiddle neck the neck's contour meets the index
finger's top between its tip lobe and the thumb tip (a local rebuild of the
kit thumb, 2.5–4 px shorter, was tried: its tip then lies over the neck
instead of the paper and heal trims the hand's outline — reverted).
"""
from __future__ import annotations

import shapely

from deck import courtkit as K
from deck.motifs import core as C


def fiddle_arm(wrist, lean, left, right, hide, *, depth=30.0, cuff=None, length=140.0, width=52.0):
    """(forearm, cuff) Parts for the figure's LEFT forearm under the fiddle
    hand: a kit sleeve rising from behind the fiddle body to ``wrist`` (the
    hand's wrist point, on the cuff's top edge), leaning ``lean``° from the
    vertical (+: the elbow down and to the LEFT, behind the body). The cuff's
    top edge runs ``left`` px to the left of the wrist point (its inner end
    under the neck) and ``right`` px to the right (a flare past the wrist);
    it is ``depth`` deep, so its lower edge lies well behind the upper bout
    (the bout covers it, the cuff's outer side runs in behind the bout at a
    clear angle: no cuff edge along the bout). The forearm is kept only
    inside ``hide`` (the region the body covers) and under the cuff (no lip
    above the cuff's sagged top edge). → (forearm, cuff, u) with ``u`` the
    unit direction from the wrist toward the elbow."""
    import math
    import numpy as np
    a = math.radians(lean)
    u = np.array([-math.sin(a), math.cos(a)])           # wrist → elbow
    n = np.array([math.cos(a), math.sin(a)])            # along the cuff's top edge, left → right
    W = np.asarray(wrist, float)
    Wc = W + n * (right - left) / 2.0                   # the cuff's top-edge centre
    base = Wc + u * length
    arm, cf = K.sleeve(K.SleeveSpec(base=tuple(base), wrist=tuple(Wc), sag=0.0, width=width,
                                    wrist_w=left + right, cuff=depth if cuff is None else cuff, folds=0,
                                    color=K.JADE, cuff_color=K.RED))
    sh = arm.shape.intersection(K.U(hide, cf.shape))
    sh = max(K._polys_of(sh), key=lambda g: g.area)
    return K.Part(sh, K.fill(sh, K.JADE), K.outline(sh), arm.meta), cf, u


def seat_on_neck(sc, name, hand, neck_shape, cuff_shape, *, shaft_x, y_fingers, back_x0=None, reach=30.0,
                 own_cut=False, back_close=None):
    """Add the tucked kit fist ``hand`` to ``sc`` as ``name`` with its heel
    closed onto the neck (and, with ``back_x0``, its back swept convex from
    the knuckle corner into the cuff).

    ``shaft_x``: the neck's axis; ``y_fingers``: the finger block's lower
    edge; the heel pocket is closed down to the cuff (``cuff_shape``), at
    most ``reach`` px below the fingers."""
    if own_cut:
        # the wrist cut exactly on the cuff's own edge (the kit would re-aim the wrist along the
        # cuff's normal; this cuff is seen obliquely, the wrist keeps its own sweep)
        hp = hand.hand
        # (0.6 px into the cuff: a cut exactly on the cuff's edge leaves zero-width slits in the
        # silhouette union, stroked at CONTOUR as knobs along the junction)
        hs = max(K._polys_of(hp.shape.difference(cuff_shape.buffer(-0.6))), key=lambda g: g.area)
    else:
        hp = hand.tucked(sc)
        hs = hp.shape
    # the pocket between the heel, the neck's edge and the cuff: hand (the heel on the neck)
    zone = K.box(shaft_x, y_fingers - 3.0, shaft_x + 24.0, y_fingers + reach).difference(cuff_shape)
    both = K.U(hs, neck_shape, cuff_shape)
    closed = both.buffer(10.0, quad_segs=12).buffer(-10.0, quad_segs=12)
    gap = closed.difference(both).intersection(zone)
    shape = K.U(hs, gap.buffer(0.9).difference(neck_shape.buffer(-0.3)).difference(cuff_shape.buffer(-0.6)))
    shape = shape.buffer(0.2).buffer(-0.2)
    shape = max(K._polys_of(shape), key=lambda g: g.area)
    if back_x0 is not None:
        backz = K.box(back_x0, y_fingers - 45.0, back_x0 + 50.0, y_fingers + reach).difference(cuff_shape)
        if back_close:
            # the back of the hand: the dip where the knuckle round meets the wrist's sweep filled
            # (a closing: the curve stays a curve, only the concave kink goes)
            cl = shape.buffer(back_close, quad_segs=16).buffer(-back_close, quad_segs=16)
            shape = K.U(shape, cl.intersection(backz))
        else:
            # the back of the hand: one convex sweep from the knuckle corner into the cuff
            shape = K.U(shape, shape.intersection(backz).convex_hull.intersection(backz))
        shape = max(K._polys_of(shape.buffer(0)), key=lambda g: g.area)
    if own_cut:
        shape = max(K._polys_of(shape.difference(cuff_shape.buffer(-0.6))), key=lambda g: g.area)
    inner = hp.meta["inner"]
    sc.add(name, K.outline(shape) + inner, shape)
    return shape


def heel_paper(sc, name, hand_shape, attr_shape, *, halo, only, arms, box, close=8.0):
    """An empty item (stack it just before the hand) whose paper channel
    clears ``only`` (items behind) in the pocket between the hand's heel,
    the attribute's own paper channel (``attr_shape`` grown by ``halo`` +
    MEDIUM/2) and the arm (``arms``: regions left alone), inside ``box``
    (x0, y0, x1, y1): the pocket where it is narrower than 2 × ``close``."""
    A = attr_shape.buffer(halo + K.MEDIUM / 2, quad_segs=12)
    arm = K.U(*arms)
    both = K.U(A, hand_shape, arm)
    gap = both.buffer(close, quad_segs=12).buffer(-close, quad_segs=12).difference(both)
    gap = gap.intersection(K.box(*box)).difference(arm)
    pieces = [g for g in K._polys_of(gap) if g.area > 2.0 and g.distance(A) < 0.6 and g.distance(hand_shape) < 0.6]
    if not pieces:
        return None
    gap = shapely.union_all(pieces)
    occ = hand_shape.intersection(gap.buffer(2.0, quad_segs=8))
    if occ.is_empty:
        return None
    sc.add(name, C.Frag(), occ, sil=False, halo=halo, halo_only=tuple(only),
           halo_zone=gap.union(occ))
    return gap



def smooth_back(hand, sc, zone, r, *, cuff=None):
    """The kit ``hand`` tucked into its arm (``Hand.tucked``) with the dip
    where the knuckle round meets the wrist's sweep filled inside ``zone``
    (a closing of radius ``r``: the back stays a curve, only the concave
    kink goes; the cuff region ``cuff`` is left alone). → a K.Hand with
    ``stub`` 0 (already tucked) for ``Hand.add_to``."""
    hp = hand.tucked(sc)
    z = zone if cuff is None else zone.difference(cuff)
    cl = hp.shape.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)
    shape = max(K._polys_of(K.U(hp.shape, cl.intersection(z)).buffer(0)), key=lambda g: g.area)
    part = K.Part(shape, hp.fills, K.outline(shape) + hp.meta["inner"], dict(hp.meta))
    return K.Hand(part, hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, 0.0)
