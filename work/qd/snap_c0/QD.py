"""art/QD.py — Q♦ · The Queen of Scales (House of the Ford), creative brief §H.11.

Justice of the square, after the figure on the courthouse dome: she weighs
the kingdom's water, and this Justice sees. 3/4 right, eyes open and level.

(composition plan: see the table below; pass q1)
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K          # noqa: E402
import _qd_parts as Q                   # noqa: E402
import _qd_hair as H                    # noqa: E402
import _qd_regalia as RG                # noqa: E402

HEAD = (372.0, 206.0)
AXF = HEAD[0] + 0.12 * 84.0             # the face's feature axis (3/4 right: +12 % of the head width)
NECK_X = 380.0

CAPE_L = [(350.0, 284.0), (290.0, 296.0), (220.0, 318.0), (190.0, 346.0), (172.0, 420.0), (158.0, 548.0)]
CAPE_R = [(414.0, 284.0), (478.0, 296.0), (546.0, 316.0), (574.0, 344.0), (590.0, 420.0), (602.0, 548.0)]
OPEN_L = [(348.0, 298.0), (316.0, 348.0), (276.0, 430.0), (244.0, 548.0)]
OPEN_R = [(418.0, 298.0), (446.0, 348.0), (478.0, 430.0), (504.0, 548.0)]
NECK_L, NECK_R, NECK_SAG = (344.0, 306.0), (424.0, 306.0), -8.0

STAFF_X = 528.0
FIST_R = (STAFF_X, 408.0)
WL, WR = (226.0, 470.0), (512.0, 442.0)
JAW = (19.0, 47.0)                      # chin circle radius, its centre below the egg centre
FACE_OVERRIDES = {}                     # face-study hook (work/qd/face_test.py); empty in the deck
PB_BASE, PB_TIP = (240.0, 462.0), (212.0, 222.0)


def _on_stem(y):
    (x0, y0), (x1, y1) = PB_BASE, PB_TIP
    return (x0 + (x1 - x0) * (y - y0) / (y1 - y0), y)


def figure():
    sc = K.Scene(rank="Q")
    fkw = dict(sex="f", age="adult", lids="level", mouth_hw=9.0, bow_rise=2.0, bow_sag=-0.5, lip_hw=4.8,
               lip_sag=-1.8, lip_dy=44.0, flick=2.5, brow_dy=-13.5, brow_sag=3.4)
    fkw.update(FACE_OVERRIDES)
    fc = K.face(HEAD, "3/4-right", **fkw)
    # a queen's jaw: the kit egg with a smaller chin circle set a little lower
    # (the skull and the eye line are unchanged; the jaw 2-3 px slimmer)
    hd, _info = K.egg(HEAD, 42.0, chin_dx=0.12 * 84.0 * 0.55, chin_r=JAW[0], chin_dy=JAW[1])
    fc.head, fc.skin = hd, K.R(hd)

    # ---- body, back to front ------------------------------------------------------
    sc.part("collar", K.standing_collar(NECK_X, top_y=226.0, half_w=108.0, neck_y=268.0, shoulder=(-134.0, 320.0),
                                        top_sag=8.0, side_sag=-5.0, rim=9.0, depth=60.0, color=K.JADE,
                                        rim_color=K.GOLD))
    cp = Q.cape(CAPE_L, CAPE_R, OPEN_L, OPEN_R, field=dict(pitch=(22.0, 19.0), stone=(8.0, 5.5), border=22.0),
                lining=14.0, band_in=21.0)
    sc.part("cape", cp)
    sc.part("lock-back", H.lock([(312.0, 238.0), (300.0, 286.0), (290.0, 334.0), (290.0, 368.0)], 24.0, 17.0,
                                n=1, side=+1))
    sc.part("neck", H.neck_chest(NECK_X, top=236.0, hw=14.5, base_y=284.0, shoulder=(346.0, 420.0),
                                 spring_y=298.0))
    stom = RG.stomacher(AXF + 1.0, top=350.0, hw_top=30.0, hw_bot=27.5)
    gw = Q.gown3(cp.meta["opening"], NECK_L, NECK_R, NECK_SAG, avoid=stom.shape)
    sc.part("gown", gw)
    sc.part("stomacher", stom)
    sc.part("clasp", K.lion_clasp((AXF + 1.0, 318.0), 40.0))

    # ---- head ------------------------------------------------------------------------
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("hair-far", H.tress(
        [(398.0, 181.0), (410.0, 190.0), (415.0, 208.0), (413.0, 232.0), (407.0, 252.0), (411.0, 272.0),
         (417.0, 298.0)],
        [(404.0, 157.0), (422.0, 170.0), (432.0, 194.0), (434.0, 224.0), (431.0, 252.0), (436.0, 278.0),
         (440.0, 300.0)], n=1, side=-1))
    sc.part("hair", H.tress(
        [(394.0, 181.0), (366.0, 184.0), (348.0, 196.0), (340.0, 218.0), (343.0, 242.0), (350.0, 258.0),
         (348.0, 278.0), (340.0, 312.0), (330.0, 352.0), (326.0, 392.0)],
        [(366.0, 152.0), (340.0, 158.0), (318.0, 176.0), (306.0, 204.0), (306.0, 234.0), (314.0, 258.0),
         (318.0, 282.0), (312.0, 318.0), (302.0, 356.0), (302.0, 394.0)], n=4, side=-1,
        guide_pts=[(356.0, 188.0), (342.0, 208.0), (339.0, 236.0), (342.0, 262.0), (340.0, 290.0), (334.0, 322.0),
                   (327.0, 360.0), (324.0, 396.0)]))
    sc.part("diadem", RG.portico(AXF + 2.0, xl=322.0, xr=428.0, top_l=166.0, top_c=172.0, top_r=168.0,
                                          col_w=10.0, pitch=20.0, cap_over=2.0, cap_h=0.0, vy=900.0, ent_h=8.0,
                                          ped_over=5.0, ped_rise=30.0, oculus_r=6.8, oculus_at=0.36))

    # ---- arms and attributes -------------------------------------------------------------
    slL, cfL = K.sleeve(K.SleeveSpec(base=(200.0, 552.0), wrist=WL, sag=5.0, width=48.0, wrist_w=32.0, cuff=14.0,
                                     color=K.JADE, cuff_color=K.GOLD))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(540.0, 552.0), wrist=WR, sag=-4.0, width=46.0, wrist_w=32.0, cuff=14.0,
                                     color=K.JADE, cuff_color=K.GOLD))
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    bal = RG.balance(STAFF_X, half=60.0, collars=(236.0, 300.0), pan_hw=23.0, surf_ry=13.0, pan_depth=7.0,
                     foot=None, beam_h=(16.0, 11.0), boss_r=8.0, staff_hw=8.0)
    sc.part("staff", bal["staff"], halo=K.HALO, halo_only=("cape", "gown"))
    sc.part("beam", bal["beam"])
    sc.add("cords", bal["cords"].lines, None, sil=False)
    sc.part("panL", bal["panL"], sil=False)
    sc.part("panR", bal["panR"], sil=False)
    pb = Q.paintbrush5(PB_BASE, PB_TIP, spike=92.0, spread=40.0, top=(26.0, 14.0),
                       bracts=((0.00, -1, 30.0, 15.0, 0.42), (0.12, +1, 30.0, 15.0, 0.45), (0.27, -1, 28.0, 14.5, 0.5),
                               (0.39, +1, 26.0, 14.0, 0.55), (0.52, -1, 23.0, 13.5, 0.62), (0.62, +1, 20.0, 13.0, 0.7)),
                       leaves=((0.40, -1, 32.0, 9.0), (0.70, +1, 30.0, 9.0)))
    sc.part("paintbrush", pb, sil=False, halo=K.HALO, halo_only=("gown", "cape", "sleeveL", "hair"))
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    ang = math.degrees(math.atan2(PB_TIP[1] - PB_BASE[1], PB_TIP[0] - PB_BASE[0]))
    K.fist(_on_stem(440.0), ang, shaft_w=8.0, back=-1, wrist=WL, wrist_w=24.0, h=32.0, knuckle=10.0, reach=6.0,
           thumb_r=5.6).add_to(sc, "handL", halo=0.0)
    K.fist(FIST_R, -90.0, shaft_w=16.0, back=-1, wrist=WR, wrist_w=24.0, h=33.0, knuckle=10.0, reach=6.0,
           thumb_r=5.6).add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "Q")
    return sc


def build():
    return figure().layers()
