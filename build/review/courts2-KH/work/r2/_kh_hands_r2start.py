"""art/_kh_hands.py — K♥ · The Ferryman King: local refinements of the kit fists.

The kit (``deck.courtkit.fist``) is shared by all twelve courts; changes the
K♥ needs are made here, on the built ``Hand``, and survive the kit's own
re-aiming of the wrist in ``Hand.tucked`` (the ``rebuild`` hook is wrapped).

    straight_heel   the ulnar edge of a fist (little-finger side, from the
                    shaft to the wrist) as one straight, slightly convex run:
                    the kit's heel curve falls back to a straight chord when
                    the wrist is bent past ≈ 45°, which leaves a Λ notch (a
                    red V sliver at card size) between the finger block's
                    underside and the heel. Filled with the convex hull of the
                    heel region, below the line block-corner → wrist.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import shapely
from shapely.geometry import Polygon

from deck import courtkit as K
from deck.motifs import core as C

P = K.P


def _frame(at, axis_deg, shaft_w, back, h):
    g = K.fist_geom(at, axis_deg, shaft_w=shaft_w, back=back, h=h)
    ax, dn = np.asarray(g["axis"], float), np.asarray(g["down"], float)
    o = P(at)

    def S(lx, ly):
        return o + lx * ax + ly * dn

    def L(q):
        q = P(q) - o
        return P(float(q @ ax), float(q @ dn))
    return g, S, L


def straight_heel(hand: K.Hand, at, axis_deg, *, shaft_w, back, h, clear=0.4, depth=40.0, round_r=1.6):
    """``hand`` with the concave notch on its heel (below the finger block,
    knuckle side of the shaft) filled: the ulnar edge runs straight from the
    block's lower corner at the shaft to the wrist. ``clear``: px the fill
    keeps off the shaft's edge line (local x ≥ shaft_w/2 + clear)."""
    g, S, L = _frame(at, axis_deg, shaft_w, back, h)
    a, y1 = float(g["a"]), float(g["y1"])
    Wl = L(hand.wrist)

    def fix_shape(shape):
        # the heel zone: knuckle side of the shaft, from 4 px inside the block's
        # underside down to the wrist, below the chord block corner -> wrist centre
        c0 = P(a + clear, y1 - 4.0)
        dirv = Wl - c0
        nrm = P(dirv[1], -dirv[0]) / max(float(np.hypot(*dirv)), 1e-6)   # points to the thumb side (−y)
        if nrm[1] > 0:
            nrm = -nrm
        far = c0 + dirv * 3.0
        zl = [c0, P(a + clear, y1 + depth), far - nrm * depth, far]
        zone = Polygon([tuple(S(*q)) for q in zl]).buffer(0)
        part = shape.intersection(zone)
        if part.is_empty:
            return shape
        fill = part.convex_hull.intersection(zone)
        new = shape.union(fill)
        if round_r:
            # round the two ends of the new edge, only there (the fingertip notches stay crisp)
            closed = new.buffer(round_r, quad_segs=10).buffer(-round_r, quad_segs=10)
            new = new.union(closed.intersection(zone.buffer(2.0)))
        if new.geom_type != "Polygon":
            new = max(K._polys_of(new), key=lambda gg: gg.area)
        return new

    def fix_part(pt: K.Part) -> K.Part:
        shp = fix_shape(pt.shape)
        meta = dict(pt.meta)
        if "rebuild" in meta:
            meta["rebuild"] = rebuild
        inner = meta.get("inner", C.Frag())
        return K.Part(shp, pt.fills, K.outline(shp) + inner, meta)

    orig = hand.hand.meta.get("rebuild")

    def rebuild(u_screen):
        return fix_part(orig(u_screen))

    return replace(hand, hand=fix_part(hand.hand))
