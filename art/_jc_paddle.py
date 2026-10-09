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






def paddle3(x=548.0, *, tip=100.0, hw=31.0, widest=158.0, shoulder=236.0, throat=282.0, loom_hw=11.0,
            bottom=545.0, band=(196.0, 216.0), tip_guard=0.0, hatch_side=+1, grip_rings=((300.0, 3),),
            ferrule=10.0, square=0.0, taper=0.62, blade_color=None):
    """The J♣ canoe paddle, blade UP like a halberd (§H.9), a racing blade:
    a broad rounded tip, the blade widest a third of the way down, straight
    shoulders tapering to the throat, a gold loom. The blade is paper split
    on its spine (MEDIUM) with ONE half hatched at 45° (§B.2) above a broad
    GOLD band that crosses the blade below its widest part (the painted band
    of a racing paddle); the spine stops at the band on both sides, so band
    and spine never read as a cross. Below the band the throat is plain. A
    gold ferrule collar (``ferrule`` tall) joins the blade to the loom, which
    carries FINE bindings (``grip_rings``: (y, n)). → Part (meta 'blade',
    'loom', 'band')."""
    t = tip
    if square:
        # a racing blade: a flatter tip rounding into straight, slightly
        # flaring sides (``square`` = the corner's drop below the tip)
        right = [P(x, t), P(x + hw * 0.62, t + square * 0.30), P(x + hw * 0.93, t + square),
                 P(x + hw, widest), P(x + hw * 0.93, widest + (shoulder - widest) * 0.55),
                 P(x + hw * taper, shoulder), P(x + loom_hw + 2.0, throat)]
    else:
        right = [P(x, t), P(x + hw * 0.72, t + 10.0), P(x + hw * 0.97, t + (widest - t) * 0.62), P(x + hw, widest),
                 P(x + hw * 0.86, widest + (shoulder - widest) * 0.55), P(x + hw * taper, shoulder),
                 P(x + loom_hw + 2.0, throat)]
    dR = K.spline(right, h_start=0.0, h_end=100.0)
    left = [P(2 * x - p[0], p[1]) for p in right][::-1]
    dL = K.spline(left, h_start=-100.0, h_end=0.0)
    ring = np.vstack([C.sample_d(dR, 0.3)[0][0], [[x + loom_hw + 2.0, throat + 1.0], [x - loom_hw - 2.0, throat + 1.0]],
                      C.sample_d(dL, 0.3)[0][0]])
    blade = Polygon(ring).buffer(0)
    fy0 = throat - ferrule * 0.5
    fer = K.R(K.rrect(x - loom_hw - 3.5, fy0, x + loom_hw + 3.5, fy0 + ferrule, 3.0))
    loom = K.box(x - loom_hw, fy0 + 2.0, x + loom_hw, bottom)
    shape = K.U(blade, loom, fer).buffer(0.6, join_style=1).buffer(-0.6, join_style=1)
    bandr = blade.intersection(K.box(0, band[0], 2000, band[1]))
    lines = C.Frag()
    lines += K.outline(shape)
    lines += K.clip_out(K.outline(blade), fer, eps=-0.5, trap=0.0)
    # its own role, like the band's: a held paddle keeps the collar's edge across the throat
    lines += K.outline(fer, role="ferrule")
    # the band's edges are its own role: a held paddle keeps them (hatch then ends on a line, not on bare gold)
    lines += K.clip_in(K.outline(bandr, role="band"), blade.buffer(-0.5))
    # the spine runs from the tip outline: the painted half's edge is never bare
    lines += K.seg(P(x, t), P(x, band[0]), MEDIUM, role="spine")
    lines += K.seg(P(x, band[1]), P(x, fy0), MEDIUM, role="spine")
    half = blade.intersection(K.box(x, 0, 2000, band[0]) if hatch_side > 0 else K.box(0, 0, x, band[0]))
    lines += K.hatch_in(half, angle=-45.0)
    gold = [loom.difference(blade).difference(fer), bandr, fer]
    if tip_guard:
        tg = blade.intersection(K.box(0, 0, 2000, t + tip_guard))
        gold.append(tg)
        lines += K.clip_in(K.outline(tg), blade.buffer(-0.5))
    fills = C.Frag()
    if blade_color:
        # a painted blade: the UNHATCHED half of the blade above the band in
        # ``blade_color`` (the split shape: one half painted, one hatched)
        plain = blade.intersection(K.box(0, 0, x, band[0]) if hatch_side > 0 else K.box(x, 0, 2000, band[0]))
        fills += K.fill(plain.difference(K.U(*gold)), blade_color)
    fills += K.fill(K.U(*gold), GOLD)
    for y0, n in grip_rings:
        for k in range(n):
            y = y0 + k * 6.3
            lines += K.clip_in(K.seg(P(x - loom_hw - 3, y), P(x + loom_hw + 3, y), FINE, role="binding"),
                               loom.buffer(-0.3))
    return K.Part(shape, fills, lines, {"blade": blade, "loom": loom, "band": bandr, "ferrule": fer})
