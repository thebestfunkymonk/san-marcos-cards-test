"""art/_jh_hands.py — the J♥ minstrel's hands, seated on the kit fists.

Local helpers for art/JH.py only (deck/courtkit.py is shared; nothing here
changes it). Both hands are kit fists (§H.0 mitten, 3 finger lines, thumb over
the top); what this module adds is where and how they meet the arm and the
held object:

* ``fiddle_arm`` — the figure's LEFT forearm under the fiddle hand: a kit
  sleeve (jade forearm, Gill Red cuff — the same arm as the bow hand's) whose
  forearm is kept only where the fiddle body hides it. What shows is the red
  cuff tucked under the fist, its inner end behind the neck, its lower edge
  running on behind the upper bout: the arm rises from behind the fiddle.
* ``seat_on_neck`` — stacks the fiddle fist tucked into that cuff with its
  HEEL run on to the neck's edge (the palm's heel pressed against the neck).
  The kit keeps a heel 7.3 px off a shaft, which beside a CONTOUR-edged neck
  leaves a 1 px paper slot between two CONTOURs that prints as an ink block;
  here the pocket between heel, neck and cuff is hand. The back of the hand
  is swept convex from the knuckle corner into the cuff (the short wrist of
  a hand straight above its cuff otherwise kinks where the kit's knuckle
  round meets the wrist taper).
* ``heel_paper`` — the bow hand: the kit turns the ground between a heel and
  a haloed shaft to paper, but not where that ground is an item named like an
  arm (the puff ``sleeveL`` behind the bow hand), which left a 3 px jade
  sliver between the heel's contour and the frog's paper channel; this adds
  the same paper channel for it.

The kit's thumb/index construction is kept as drawn on every court (one
hand language): on the narrow fiddle neck the neck's contour meets the index
finger's top between its tip lobe and the thumb tip.
"""
from __future__ import annotations

import shapely

from deck import courtkit as K
from deck.motifs import core as C


def fiddle_arm(wrist_c, base, width, cuff_w, hide, *, cuff=12.0):
    """(forearm, cuff) Parts: a kit sleeve from ``base`` up to ``wrist_c``
    (the cuff's top-edge centre), ``cuff_w`` wide at the wrist; the forearm is
    clipped to ``hide`` (the region the fiddle body covers, plus the strip
    just under the cuff that may show)."""
    arm, cf = K.sleeve(K.SleeveSpec(base=tuple(base), wrist=tuple(wrist_c), sag=0.0, width=width,
                                    wrist_w=cuff_w, cuff=cuff, folds=0, color=K.JADE, cuff_color=K.RED))
    sh = arm.shape.intersection(hide)
    sh = max(K._polys_of(sh), key=lambda g: g.area)
    return K.Part(sh, K.fill(sh, K.JADE), K.outline(sh), arm.meta), cf


def seat_on_neck(sc, name, hand, neck_shape, cuff_shape, *, shaft_x, y_fingers, y_cuff, back_x0):
    """Add the tucked kit fist ``hand`` to ``sc`` as ``name`` with its heel
    closed onto the neck and its back swept convex into the cuff.

    ``shaft_x``: the neck's axis; ``y_fingers``: the finger block's lower
    edge; ``y_cuff``: the cuff's top edge; ``back_x0``: the x from which the
    back of the hand (knuckle side) is swept convex."""
    hp = hand.tucked(sc)
    hs = hp.shape
    # the pocket between the heel, the neck's edge and the cuff: hand (the heel on the neck)
    zone = K.box(shaft_x, y_fingers - 3.0, shaft_x + 24.0, y_cuff + 6.0)          # the heel side only
    both = K.U(hs, neck_shape, cuff_shape)
    closed = both.buffer(10.0, quad_segs=12).buffer(-10.0, quad_segs=12)
    gap = closed.difference(both).intersection(zone)
    shape = K.U(hs, gap.buffer(0.4).difference(neck_shape.buffer(-0.3))).buffer(0.2).buffer(-0.2)
    shape = max(K._polys_of(shape), key=lambda g: g.area)
    # the back of the hand: one convex sweep from the knuckle corner into the cuff
    backz = K.box(back_x0, y_fingers - 45.0, back_x0 + 50.0, y_cuff - 1.0)
    shape = K.U(shape, shape.intersection(backz).convex_hull.intersection(backz))
    shape = max(K._polys_of(shape.buffer(0)), key=lambda g: g.area)
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
