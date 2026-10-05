"""art/_qh_hand.py — a queen's hand laid flat on the bodice (§H.0 mitten).

The kit's ``flat()`` is a square-ended mitten — right for a king's hand on a
hilt, stiff on a queen's breast. This is the same §H.0 construction (a
mitten, three MEDIUM finger lines, a separate thumb) drawn slimmer and
tapered, with the fingertips on an oblique curve (middle finger longest,
little finger shortest) so the hand reads as relaxed and feminine:

* back of the hand: a rounded trapezoid from the wrist to the knuckles;
* four finger capsules (Ø ``width``/4) from the knuckle line to rounded tips;
  their union's outline gives the small valleys between the tips;
* three MEDIUM finger lines from those valleys back toward the knuckles;
* the THUMB a separate capsule along the thumb-side edge, pointing to the
  tips, drawn in front of the hand (``Hand.add_to`` stacks it).

Upstream candidate: ``courtkit.flat(..., taper=, slant=)`` for queens.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck.motifs import core as C

P = K.P
MEDIUM = K.MEDIUM


def lady_hand(wrist, angle, *, length=60.0, width=28.0, wrist_w=22.0, side=-1, tips=(3.0, 0.0, 2.5, 8.0),
              knuckle=0.50, thumb_r=5.4, thumb=(0.16, 0.60), thumb_out=2.0, curl=0.0, vgap=4.0) -> K.Hand:
    """A hand from ``wrist`` pointing ``angle`` (screen degrees). ``side`` −1:
    the thumb on the screen-left of the pointing direction. ``tips``: how far
    each fingertip stops short of ``length`` (index, middle, ring, little —
    from the thumb side). ``curl`` > 0 bends the finger columns toward the
    little-finger side by that many degrees (a softly closing hand)."""
    L = float(length)
    hw = width / 2
    fw = width / 4
    ts = -1.0 if side < 0 else 1.0           # local y of the thumb side
    xk = L * knuckle
    # back of the hand: wrist → knuckles
    back = Polygon([(0.0, -wrist_w / 2), (xk, -hw + 0.8), (xk, hw - 0.8), (0.0, wrist_w / 2)])
    back = back.buffer(3.0, quad_segs=10).buffer(-3.0, quad_segs=10)
    caps = []
    tip_pts = []
    for k in range(4):
        # finger 0 is on the thumb side
        yk = ts * (hw - fw / 2) - ts * k * fw
        x_end = L - tips[k] - fw / 2
        bend = math.radians(curl * (k / 3.0))
        p0 = (xk - 2.0, yk)
        p1 = (x_end, yk - ts * (x_end - xk) * math.sin(bend) * 0.5)
        caps.append(LineString([p0, p1]).buffer(fw / 2, quad_segs=16))
        tip_pts.append(np.array(p1))
    fingers = shapely.union_all(caps)
    hand = back.union(fingers).buffer(0.6, quad_segs=6).buffer(-0.6, quad_segs=6)
    lines = C.Frag()
    for k in range(1, 4):
        a, b = tip_pts[k - 1], tip_pts[k]
        valley = (a + b) / 2
        valley[0] = min(a[0], b[0])                # the V between the two tip arcs
        p_start = P(valley[0] - vgap, valley[1])
        p_end = P(xk + 3.0 + (2.0 if k == 2 else 0.0), valley[1])
        if p_start[0] - p_end[0] > 6.0:
            lines += K.seg(p_start, p_end, MEDIUM, role="finger")
    # thumb: a capsule along the thumb-side edge toward the tips
    t0 = (L * thumb[0], ts * (wrist_w / 2 - 1.0))
    t1 = (L * thumb[1], ts * (hw + thumb_out))
    th = LineString([t0, t1]).buffer(thumb_r, quad_segs=16)
    M, Mf = K._rigid(wrist, angle, mirror_x=False)
    hand_s, thumb_s = K._xf(hand, M), K._xf(th, M)
    hl = (K.outline(hand) + lines).transformed(Mf)
    tl = K.outline(th).transformed(Mf)
    return K.Hand(K.Part(hand_s, C.Frag(), hl, {"kind": "flat"}), K.Part(thumb_s, C.Frag(), tl, {}), P(wrist),
                  wrist_w)
