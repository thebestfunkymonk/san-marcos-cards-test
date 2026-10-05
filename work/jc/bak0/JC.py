"""art/JC.py — J♣ · The River Squire (House of the Reed), creative brief §H.9.

Built with deck.courtkit (the K♠'s hand) plus art/_jc_parts.py for the parts
the kit does not have (brimmed cap, heron plume, paddle, jerkin, pecan work).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K  # noqa: E402
from deck.motifs import core as C  # noqa: E402
from deck.motifs import geometric as MG  # noqa: E402
import _jc_parts as J  # noqa: E402

HEAD = (385.0, 207.0)
PADDLE_X = 550.0
FIST = (550.0, 400.0)


def sprays_ko(region, paths, *, w=K.MEDIUM, pitch=9.0, tick=11.0):
    """Comb sprays (§G.18) along ``paths``, knocked out of a jade region."""
    f = C.Frag()
    for p in paths:
        f += MG.comb_spray(p, pitch=pitch, tick=tick, angle=52.0, w=w)
    reg = K.R(region)
    f = K.clip_in(f, reg.buffer(-(K.MEDIUM / 2 + 3.2)))
    return C.knockout(K.D(reg), f)


def figure():
    sc = K.Scene(rank="J")
    fc = K.face(HEAD, "3/4-left", age="young", lids="level", pupil_dx=-3.5, brow_dy=-12.5, brow_sag=3.6,
                mouth_hw=9.5)

    # ---- body, back to front ----------------------------------------------------
    doub = J.doublet()
    arms = doub.shape.difference(J.jerkin(doub.shape).shape.buffer(-0.5))
    ko = sprays_ko(doub.shape, ["M221 344L208 505", "M546 340L560 505"])
    sc.add("doublet", K.fill(ko, K.JADE) + doub.lines, doub.shape)
    jer = J.jerkin(doub.shape)
    pk = J.placket(jer.shape)
    bl = J.belt(jer.shape)
    weave_reg = jer.shape.difference(pk.shape.buffer(3.0)).difference(bl.shape.buffer(3.0))
    leaves, nuts = J.pecan_weave(weave_reg, length=56.0, pairs=3)
    red = C.knockout(K.D(jer.shape), leaves)
    sc.add("jerkin", K.fill(red, K.RED) + jer.lines, jer.shape)
    sc.add("nuts", nuts, None, sil=False)
    sc.part("placket", pk)
    sc.part("clasp", K.lion_clasp((365.0, 338.0), 40.0))
    for k, y in enumerate((373.0, 404.0, 435.0)):
        x = 366.0 - (y - 314.0) * 5.0 / 246.0
        sc.add(f"button{k}", K.fill(K.circle((x, y), 6.3), K.GOLD) + K.outline(K.circle((x, y), 6.3), K.FINE),
               K.R(K.circle((x, y), 6.3 + K.FINE / 2)), sil=False)
    sc.part("belt", bl)
    sc.part("buckle", J.pecan_husk((362.0, 462.0), style="D", s=1.2))

    # ---- head -------------------------------------------------------------------
    hs_far = K.HairSpec(top=(-40.0, -18.0), bulge=(-66.0, 40.0), bottom=(-50.0, 90.0), ribbons=5, over=4.0)
    sc.part("hair-far", K.hair_fall(fc, -1, hs_far))
    hs = K.HairSpec(top=(-48.0, -16.0), bulge=(-86.0, 38.0), bottom=(-72.0, 98.0), ribbons=6, over=6.0)
    sc.part("hair-back", K.hair_fall(fc, +1, hs))
    sc.part("neck", K.neck(fc, bottom=300.0))
    sc.part("collar", J.collar(fc))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("ear", J.ear(fc))
    sc.part("plume", J.plume([(452.0, 162.0), (474.0, 130.0), (484.0, 104.0), (498.0, 84.0), (522.0, 73.0)]))
    sc.part("cap", J.cap(fc))

    # ---- arms, paddle, hands ------------------------------------------------------
    WL, WR = (272.0, 462.0), (520.0, 440.0)
    for nm, spec in (("L", K.SleeveSpec(base=(226.0, 552.0), wrist=WL, sag=5.0, width=50.0, wrist_w=32.0, cuff=13.0,
                                        color=K.JADE)),
                     ("R", K.SleeveSpec(base=(476.0, 552.0), wrist=WR, sag=-6.0, width=52.0, wrist_w=34.0, cuff=13.0,
                                        color=K.JADE))):
        sl, cf = K.sleeve(spec)
        B, W = K.P(spec.base), K.P(spec.wrist)
        u = (W - B) / K.np.hypot(*(W - B))
        path = f"M{B[0] - u[0] * 0:.2f} {B[1]:.2f}L{W[0] - u[0] * 18:.2f} {W[1] - u[1] * 18:.2f}"
        kos = sprays_ko(sl.shape, [path])
        sc.add("sleeve" + nm, K.fill(kos, K.JADE) + K.outline(sl.shape), sl.shape)
        sc.add("cuff" + nm, cf.lines, cf.shape)
    sc.part("paddle", J.paddle(PADDLE_X), halo=K.HALO, halo_only=("doublet",))
    K.flat((WL[0] - 2.0, WL[1] - 2.0), 2.0, side=-1).add_to(sc, "handL", halo=0.0)
    K.fist(FIST, -90.0, shaft_w=26.0, back=-1, wrist=WR, wrist_w=26.0, h=36.0).add_to(sc, "handR", halo=0.0)
    return sc


def build():
    return figure().layers()
