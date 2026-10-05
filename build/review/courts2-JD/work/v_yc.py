"""art/JD.py — J♦ · The Herald of the Road (House of the Ford), creative brief §H.12.

The court's messenger on El Camino Real, announcing arrivals at the crossing.
3/4 RIGHT; lips closed, gaze along the trumpet. Built with deck.courtkit (the
K♠'s hand) plus art/_jd_parts.py (trumpet, banner, feathers, cap, tabard,
cuffs, map scroll).

Composition plan (top half, card px; the system adds clip, 180° copy, frame,
♦ ford band (plain, Jack), pips and indices):

| part     | colour | geometry |
|----------|--------|----------|
| head     | paper  | 3/4-right kit egg r 44 about (382, 207): eye line 213, chin ≈ 277; 11 face strokes |
| face     | ink    | kit 3/4-right, young, lids 'raised', pupils +3 toward the bell (gaze along the trumpet); lips closed |
| hair     | gold   | page-boy bob behind the ear (x 298–374, cap to the shoulder, 3 current lines) + a slim far lock to the jaw |
| cap      | red    | flat cap: gold band 166–186 across the brow (clear of the brows), red crown lens x 316–458 |
| brooch   | gold   | ♦ lozenge (22 × 30) on the band at (350, 180), red stone cut in; the feather roots start under it |
| feathers | paper  | two forked scissor-tail feathers from the brooch, trailing back: upper to (262, 66), lower to (204, 266); 22 wide, one current line each, red tips behind a MEDIUM chevron; ≥ 12 px clear of the pip |
| doublet  | jade   | V-neck (386, 340) + standing collar 279–303 |
| tabard   | red    | T-shaped herald's tabard: shoulders 300–326, flaps to x 190 / 574 (y 378), panel x 282–490; §G.23 stepping-stone chain KNOCKED OUT round every edge (as the Q♦ cape); gold rowels r 11.5 (solid, Aquifer contour) in a half-drop grid (32 × 30) on the open chest |
| belt     | gold   | 441–473, §G.31 tooled scroll as ONE row of large eye volutes (r0 8.6) on a running stem, a sessile vesica leaf between each two: two whole volutes show between the buckle and the right cuff; ♦ lozenge buckle (38 × 36, red stone) at (394, 457) |
| sleeves  | jade   | doublet sleeves under the flaps to x 150 / 606, K♦ ford-stone brocade (28 × 24) |
| cuffs    | gold   | flared gauntlets, one unit of the belt's scroll each (stem, eye volute, leaf); the left one's sits under the band |
| trumpet  | gold   | the LONG STRAIGHT herald's trumpet: axis −63°, bell mouth centre (584, 124) (bell centroid ≈ (577, 146); the frame clip stops it nearer x 590), a modest trumpet flare 48 long / mouth 45 with the mouth dark, a split line; tube 18 to s 327 with a bead knop at the bell, ~40 px of plain tube above the banner, ball boss s 240, ferrule s 272; paper halo over the tabard |
| banner   | jade   | 110 × 90 from a gold rod lashed across the tube at s 88 (y ≈ 202), x 470–580 (the tube runs behind it and out through the bottom edge); FINE seam; Lion Mark 60 px (§G.2 simplified mark ≤ 60, lion_clasp construction); §G.14 drip fringe right of the tube |
| hands    | paper  | fist on the trumpet at y 394; fist on the map's left roller at (272, 462) |
| map      | paper  | held open between two gold rollers x 272–370 × y 436–494: triple wavy river crossed by the dotted route |
"""
from __future__ import annotations

import os
import sys

import numpy as np
from shapely.geometry import Polygon

sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")

from deck import courtkit as K  # noqa: E402
import _jd_parts as J  # noqa: E402
import _jd_hands as H  # noqa: E402

P = K.P
HEAD = (382.0, 207.0)
MOUTH = (584.0, 124.0)             # the trumpet bell's mouth centre
AXIS = -63.0
LASH = 88.0                        # the banner rod lashes to the tube here (s from the mouth)
BANNER = (74.0, 36.0, 90.0)        # the banner: left and right of the rod's crossing, drop from the rod
BELT = (441.0, 473.0)              # the belt's top and bottom
# §G.31 on the belt: one row of eye volutes, a sessile leaf between each two (J.running_scroll)
BELT_SCROLL = dict(x_first=427.5, n=2, r0=8.6, q=8.4, flat=2.5, leaf=(17.2, 6.4), pet=0.9, dy=0.3, lead_x=400.0)
CUFF_SPRIG = dict(x_first=4.5, yc=0.5, r0=8.4, q=7.0, flat=2.5, leaf=(14.0, 5.6), pet=0.9)   # one unit of it
ROWELS = dict(pitch=(32.0, 30.0), r=11.5, origin=(386.0, 348.0))   # the tabard's half-drop grid


def figure():
    sc = K.Scene(rank="J")
    # raised lids (the herald looks up along the trumpet) with the pupils showing below the RULE lid
    # (tuck 0: the kit then seats them 3 px off the lower lid), not hidden under it
    fc = K.face(HEAD, "3/4-right", age="young", lids="raised", pupil_dx=3.0, pupil_tuck=0.0)
    T = J.Trumpet(MOUTH, AXIS)

    # ================= build every part first (the tabard's rowels are placed on what stays visible)
    armL = J.spl_region([(192, 366), (240, 364), (290, 366), (292, 450), (286, 530), (156, 530), (150, 466),
                         (160, 400)])
    armR = J.spl_region([(484, 364), (570, 366), (598, 400), (606, 466), (606, 530), (484, 530), (482, 450)])
    tab_d = (K.Path((340.0, 300.0)).line((386.0, 340.0)).line((430.0, 298.0)).sag((550.0, 322.0), 3.0)
             .line((566.0, 326.0)).line((574.0, 376.0)).line((490.0, 378.0)).line((490.0, 530.0))
             .line((282.0, 530.0)).line((282.0, 380.0)).line((190.0, 378.0)).line((196.0, 324.0))
             .line((212.0, 318.0)).sag((340.0, 300.0), 3.0).close().d)
    tab = K.R(tab_d).buffer(-15.0, join_style=1).buffer(15.0, join_style=1)
    BUCKLE = (394.0, 457.0)
    buckle = J.lozenge_buckle(BUCKLE, L=36.0, W=38.0, inner=(14.0, 16.0))

    # each wrist out along its hand's axis (courtkit.fist_wrist): the forearm continues the hand
    FIST_R, _ = T.point_at_y(394.0)
    WR, BR = tuple(K.fist_wrist(FIST_R, AXIS, bend=35.0, dist=0.85, shaft_w=18.0, back=+1, h=36.0)), (548.0, 552.0)
    slR, _ = K.sleeve(K.SleeveSpec(base=BR, wrist=WR, sag=-5.0, width=56.0, wrist_w=36.0, cuff=1.0,
                                   color=K.JADE, cuff_color=K.JADE))
    tr = J.trumpet(T, tube_w=18.0, mouth_hw=22.5, bell_len=48.0, lip=6.0, flare=2.8, knop=(48.0, 8.0),
                   boss=(240.0, 12.0), ferrules=(272.0,), ferrule=(6.0, 3.2), length=327.0, mp=(8.0, 7.0, 7.0),
                   hatch_bell="split", throat_merge=True)
    rod_x, rod_y = (float(v) for v in T.at(LASH))
    bl, br_, bh = BANNER
    bx0, bx1, by1 = rod_x - bl, rod_x + br_, rod_y + bh
    tube_x = float(T.point_at_y(by1)[0][0]) + 9.0 / abs(T.u[1]) + K.MEDIUM / 2 + 3.2 + K.TD / 2
    bn = J.banner(bx0, rod_y, bx1, by1, seam=9.0, fringe=(10.5, 9.5, 13.0), avoid=K.U(tab, tr.shape),
                  fringe_x0=tube_x)
    uR = np.array(WR) - np.array(BR)
    cuffR = J.gauntlet(WR, uR, width=38.0, flare=46.0, depth=40.0, mirror=True, sprig=CUFF_SPRIG)
    handR = K.fist(FIST_R, AXIS, shaft_w=18.0, back=+1, wrist=WR, wrist_w=24.0, h=36.0)

    # the fist closes on the thick rolled end of the map (22 wide, x 264–286): the fist is built on its
    # left 10 px, so the fingertip lobes end ON the gold roll (gold shows past them, not the paper sheet)
    FIST_L = (269.0, 460.0)
    HAND_L = dict(shaft_w=10.0, back=-1, h=34.0, reach=3.0)
    WL, BL = tuple(K.fist_wrist(FIST_L, -90.0, bend=45.0, **HAND_L)), (192.0, 566.0)
    slL, _ = K.sleeve(K.SleeveSpec(base=BL, wrist=WL, sag=4.0, width=52.0, wrist_w=34.0, cuff=1.0,
                                   color=K.JADE, cuff_color=K.JADE))
    # the sheet from the roll's axis to the right roller, clear of the buckle's tip (x 375)
    mp = J.map_open(275.0, 362.0, 434.0, 492.0, roll_l=22.0, over_l=12.0, crossing=True)
    uL = np.array(WL) - np.array(BL)
    cuffL = J.gauntlet(WL, uL, width=38.0, flare=52.0, depth=44.0, sprig=dict(CUFF_SPRIG, yc=16.0))  # under the band
    handL = K.fist(FIST_L, -90.0, wrist=WL, wrist_w=24.0, **HAND_L)

    # the belt's tooled scroll (§G.31): one row of large eye volutes between the buckle and the right cuff
    belt_box = K.box(250.0, BELT[0], 520.0, BELT[1]).intersection(tab.buffer(-0.5))
    over = K.U(buckle.shape, slR.shape, tr.shape, cuffR.shape, handR.hand.shape, handR.thumb.shape, mp.shape)
    belt = J.tooled_belt(250.0, 520.0, BELT[0], BELT[1], tab.buffer(-0.5), color=K.GOLD,
                         scroll=dict(BELT_SCROLL,
                                     keep=belt_box.difference(over.buffer(K.MEDIUM / 2 + 3.2 + K.FINE / 2))))

    front = K.U(belt.shape, buckle.shape, slR.shape, tr.shape.buffer(K.HALO + K.MEDIUM / 2), cuffR.shape,
                handR.hand.shape, handR.thumb.shape, slL.shape, mp.shape, cuffL.shape, handL.hand.shape,
                handL.thumb.shape)
    vis = tab.difference(front.buffer(1.0))
    rw = J.rowel_grid(tab.buffer(-21.6), visible=vis, clear=3.2, **ROWELS)

    # ================= the stack, back to front
    sc.part("neck", K.neck(fc, bottom=312.0, width=36.0))
    dbl = K.R(Polygon([(350.0, 292.0), (422.0, 290.0), (444.0, 356.0), (328.0, 356.0)]))
    sc.part("doublet", K.Part(dbl, K.fill(dbl, K.JADE), K.outline(dbl), {}))
    col = K.R(K.Path((352.0, 282.0)).sag((420.0, 279.0), -4.0).line((426.0, 300.0)).sag((346.0, 303.0), 7.0)
              .close().d)
    sc.part("collar", K.Part(col, K.fill(col, K.JADE), K.outline(col), {}))
    brc = dict(pitch=(28.0, 24.0), size=(12.0, 7.5), origin=(375.0, 398.0))
    sc.part("armL", J.sleeve_part(armL, [], brocade=brc))
    sc.part("armR", J.sleeve_part(armR, [], brocade=brc))
    # chain stones are whole or hidden: a stone half under the map / belt / arms is dropped (no red
    # swallow-tail flush with the map's edge)
    covers = K.U(mp.shape, belt.shape, buckle.shape, slR.shape, cuffR.shape, handR.hand.shape, slL.shape,
                 cuffL.shape, handL.hand.shape)
    sc.part("tabard", J.tabard(tab, rowels=rw, chain=dict(d_in=8.0, band=12.0, stone=11.0, pitch=20.0,
                                                          keep=tab.difference(covers.buffer(1.0)))))
    sc.part("belt", belt)
    sc.part("buckle", buckle)

    # head
    fl = J.feather([(350, 182), (310, 184), (272, 192), (240, 210), (216, 236), (204, 266)], w_max=22.0,
                   w_tip=17.0, tip=30.0, n_lines=1, side=+1)
    fu = J.feather([(350, 180), (322, 160), (298, 138), (280, 114), (268, 90), (262, 66)], w_max=22.0,
                   w_tip=17.0, tip=30.0, n_lines=1, side=-1)
    band, crown = J.flat_cap(((338, 186), (434, 182), -2.0), ((340, 166), (432, 162), -3.0),
                             ((316, 172), (458, 162), 22.0, 9.0), band_color=K.GOLD)
    hair_out = [(304, 196), (298, 224), (298, 260), (304, 288), (320, 307), (342, 315)]
    sc.part("hair", J.hair_bob([(346, 186), (336, 188), (304, 196), (298, 224), (298, 260), (304, 288), (320, 307),
                                 (342, 316), (364, 310), (374, 292), (372, 258), (362, 228), (352, 206)], hair_out,
                                n=3, side=+1, stagger=9.0, first=10.0, cut=K.U(fl.shape, band.shape),
                                visible=K.box(0, 0, 2000, 2000).difference(fc.skin.buffer(1.0))))
    sc.part("hairR", J.hair_bob([(410, 180), (432, 178), (441, 188), (445, 212), (444, 236), (437, 252), (427, 258),
                                 (418, 250), (418, 220)], [(437, 184), (444, 210), (443, 236), (434, 254)], n=1,
                                side=-1,
                                stagger=0.0, first=10.0, cut=band.shape,
                                visible=K.box(0, 0, 2000, 2000).difference(fc.skin.buffer(1.0))))
    sc.part("ear", J.ear((342.0, 227.0), r=9.5, a0=90.0, a1=270.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("featherL", fl)
    sc.part("featherU", fu)
    sc.part("capband", band)
    sc.part("cap", crown)
    sc.part("brooch", J.lozenge_buckle((350.0, 180.0), L=30.0, W=22.0, inner=(16.0, 11.0)))

    # right arm, trumpet, banner
    sc.part("forearmR", slR)
    sc.part("trumpet", tr, halo=K.HALO, halo_only=("tabard",))
    sc.part("banner", bn)
    sc.add("fringe", bn.meta["fringe"], None, sil=False)
    sc.part("rod", J.rod((bx0 - 8.0, rod_y), (bx1 + 3.0, rod_y), h=9.5, finial=5.8))
    sc.part("lion", K.lion_clasp(tuple(bn.meta["centre"] + P(0, -3.4)), 60.0))
    sc.part("cuffR", cuffR)
    # the fist's own paper channel on the tabard (it joins the trumpet's and the chain's inner rail),
    # kept clear of the panel's red rim and edge line
    H.add_haloed(sc, "handR", H.smooth_back(handR, sc, K.box(466.0, 384.0, 496.0, 430.0), 25.0, hull=True,
                                            knob_zone=K.box(443.0, 412.0, 457.0, 424.0), knob_r=2.5),
                 only=("tabard",), within=tab.buffer(-6.3), attr=tr.shape)

    # left arm, map
    sc.part("forearmL", slL)
    sc.part("map", mp)
    sc.part("cuffL", cuffL)
    handL.add_to(sc, "handL", halo=0.0)
    return sc


def build():
    return figure().layers()
