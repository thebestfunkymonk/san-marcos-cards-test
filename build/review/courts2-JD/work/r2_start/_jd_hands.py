"""art/_jd_hands.py — the J♦ herald's hands, seated on the kit fists.

Local helpers for art/JD.py only (deck/courtkit.py is shared; nothing here
changes it). Both hands are kit fists (§H.0 mitten, 3 finger lines, thumb over
the top); this module only finishes where they meet the arm:

* ``smooth_back`` — the kit fist tucked into its cuff (``Hand.tucked``) with
  the concave dip where the knuckle round meets the wrist's sweep filled
  inside a zone (a closing: the back stays one curve into the cuff, only the
  kink goes), and optionally the small knob where the finger block's
  underside meets the heel's curve rounded off (an opening inside a second
  zone). → a ``K.Hand`` with ``stub`` 0 (already tucked) for ``add_to``.
  Only the back side goes in the zone: a closing that reaches the heel
  fills the wrist's taper too (a convex hull did: the wrist read as wide as
  the knuckles).
* ``add_haloed`` — the trumpet fist stacked with its OWN paper channel on the
  tabard (the kit carries only the attribute's channel round the fingertips):
  the tabard's inner chain rail ran 2–3 px beside the fist's back, leaving red
  teeth and half stones along it. The channel is kept inside the panel's red
  rim (never opening the tabard's edge line onto the sleeve), and the ground
  between it and the trumpet's own channel is closed on a round arc under
  the heel, as the kit does for a heel beside a haloed shaft.
"""
from __future__ import annotations

from deck import courtkit as K


def _biggest(g):
    return max(K._polys_of(g.buffer(0)), key=lambda q: q.area)


def smooth_back(hand, sc, zone, r, *, knob_zone=None, knob_r=2.0):
    """``hand`` (a kit Hand) tucked into the arm already in ``sc``; the dip
    between its knuckle round and its wrist sweep closed (radius ``r``)
    inside ``zone`` (the cuff is never touched: the tuck already cut the
    wrist on the cuff's edge, and the closing is clipped off the cuff); with
    ``knob_zone``, a knob on the heel opened (radius ``knob_r``) there."""
    hp = hand.tucked(sc)
    cuffs = [it.occ for it in sc.items if it.occ is not None and not it.occ.is_empty
             and any(w in it.name.lower() for w in K.CUFF_WORDS)]
    cuff = K.U(*cuffs) if cuffs else None
    z = zone if cuff is None else zone.difference(cuff.buffer(0.6))
    cl = hp.shape.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)
    shape = _biggest(K.U(hp.shape, cl.intersection(z)))
    if knob_zone is not None:
        # a jog on the heel: closed, then opened, inside the zone only
        cl2 = shape.buffer(knob_r, quad_segs=12).buffer(-knob_r, quad_segs=12)
        shape = _biggest(K.U(shape, cl2.intersection(knob_zone)))
        op = shape.buffer(-knob_r, quad_segs=12).buffer(knob_r, quad_segs=12)
        shape = _biggest(shape.difference(knob_zone.difference(op)))
    part = K.Part(shape, hp.fills, K.outline(shape) + hp.meta["inner"], dict(hp.meta))
    return K.Hand(part, hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, 0.0)


def add_haloed(sc, name, hand, *, only, within, attr=None, close=K.HEEL_CLOSE):
    """Stack a (tucked) kit ``hand`` with its own paper channel (HALO) on the
    items ``only`` behind it, the channel kept inside ``within`` (e.g. clear
    of a panel's edge line and rim, so the channel never opens the panel's
    outline onto the ground behind it). With ``attr`` (the held object's
    region, itself haloed on the same items), the ground left between the
    two channels narrower than 2 × ``close`` turns to paper too, closing on a
    round arc (the kit's heel treatment): no cusp, no 1–3 px island."""
    hp = hand.tucked(sc)
    h = K.HALO + K.MEDIUM / 2
    g = hp.shape.buffer(h, quad_segs=12)
    if attr is not None:
        A = attr.buffer(h, quad_segs=12)
        closed = K.U(g, A).buffer(close, quad_segs=12).buffer(-close, quad_segs=12)
        g = K.U(g, closed.difference(A).intersection(hp.shape.buffer(h + 2.0 * close, quad_segs=12)))
    zone = g.intersection(within)
    sc.add(name, hp.frag, hp.shape, halo=K.HALO, halo_only=tuple(only), halo_zone=zone)
    return hp
