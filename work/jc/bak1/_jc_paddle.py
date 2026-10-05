"""art/_jc_paddle.py — J♣'s canoe paddle, held upright like a halberd (§H.9).

A beavertail blade (rounded tip, widest a third of the way down, a long
concave taper into the throat) on a gold loom. The blade is paper, split on
its spine (MEDIUM) with ONE half hatched at 45° (§B.2); a broad gold band
crosses it below the tip (the painted tip band of a racing paddle), so the
band and the spine never make a cross; the loom carries two FINE bindings.
Final size, card px (top half). → courtkit Part.
"""
from __future__ import annotations

import numpy as np
from shapely.geometry import Polygon

from deck import courtkit as K
from deck.motifs import core as C

P = K.P
INK, GOLD = K.INK, K.GOLD
FINE, MEDIUM, CONTOUR = K.FINE, K.MEDIUM, K.CONTOUR


def blade_outline(x, tip, hw, widest, throat, loom_hw, *, tip_r=0.60, neck=0.46):
    """Right half of the blade as points (top → throat) and the mirrored
    left half; ``tip_r`` = half-width at 14 px below the tip / hw; ``neck``
    = half-width 30 px above the throat / hw."""
    right = [P(x, tip), P(x + hw * tip_r, tip + 12.0), P(x + hw * 0.93, tip + (widest - tip) * 0.55),
             P(x + hw, widest), P(x + hw * 0.80, widest + (throat - widest) * 0.55),
             P(x + hw * neck, throat - 26.0), P(x + loom_hw, throat)]
    return right


def paddle(x=548.0, *, tip=92.0, hw=29.0, widest=172.0, throat=292.0, loom_hw=10.0, bottom=545.0,
           band=(114.0, 134.0), bindings=((300.0, 3), (372.0, 3)), hatch_side=+1, spine_to=None):
    right = blade_outline(x, tip, hw, widest, throat, loom_hw)
    dR = K.spline(right, h_start=0.0, h_end=92.0)
    left = [P(2 * x - p[0], p[1]) for p in right][::-1]
    dL = K.spline(left, h_start=-92.0, h_end=0.0)
    ring = np.vstack([C.sample_d(dR, 0.3)[0][0], C.sample_d(dL, 0.3)[0][0]])
    blade = Polygon(ring).buffer(0)
    loom = K.box(x - loom_hw, throat - 6.0, x + loom_hw, bottom)
    shape = K.U(blade, loom).buffer(0.8, join_style=1).buffer(-0.8, join_style=1)
    bandr = blade.intersection(K.box(0, band[0], 2000, band[1]))
    spine_bot = throat - 8.0 if spine_to is None else spine_to
    spine = K.seg(P(x, band[1]), P(x, spine_bot), MEDIUM, role="spine")
    half = blade.intersection(K.box(x, band[1], 2000, spine_bot) if hatch_side > 0
                              else K.box(0, band[1], x, spine_bot))
    hatch = K.hatch_in(half, angle=-45.0)
    loom_vis = loom.difference(blade)
    fills = K.fill(K.U(loom_vis, bandr), GOLD)
    lines = K.outline(shape) + K.clip_in(K.outline(bandr), blade.buffer(-0.5)) + spine + hatch
    # the throat seam where the blade's taper meets the loom
    lines += K.clip_in(K.seg(P(x - loom_hw - 2, throat), P(x + loom_hw + 2, throat), MEDIUM, role="throat"),
                       shape.buffer(-0.5))
    for y0, n in bindings:
        for k in range(n):
            y = y0 + k * 6.3
            lines += K.clip_in(K.seg(P(x - loom_hw - 3, y), P(x + loom_hw + 3, y), FINE, role="binding"),
                               loom.buffer(-0.3))
    return K.Part(shape, fills, lines, {"blade": blade, "loom": loom, "band": bandr})
