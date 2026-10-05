"""art/QD.py — Q♦ · The Queen of Scales (House of the Ford), creative brief §H.11.

Justice of the square, after the figure on the courthouse dome: she weighs
the kingdom's water, and this Justice sees. 3/4 right, eyes open and level.

(composition plan: pass 4 draft)
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K          # noqa: E402
import _qd_parts as Q                   # noqa: E402
import _qd_hair as H                    # noqa: E402

HEAD = (377.0, 208.0)
AXF = 387.0                             # the face's feature axis (3/4 right: +12 % of the head width)
NECK_X = 385.0

CAPE_L = [(348.0, 286.0), (282.0, 302.0), (214.0, 324.0), (184.0, 360.0), (160.0, 450.0), (150.0, 548.0)]
CAPE_R = [(426.0, 286.0), (492.0, 300.0), (550.0, 322.0), (576.0, 356.0), (592.0, 450.0), (600.0, 548.0)]
OPEN_L = [(346.0, 292.0), (318.0, 340.0), (262.0, 420.0), (226.0, 548.0)]
OPEN_R = [(428.0, 292.0), (450.0, 340.0), (470.0, 420.0), (482.0, 548.0)]
NECK_L, NECK_R, NECK_SAG = (338.0, 304.0), (436.0, 304.0), -11.0

PB_BASE, PB_TIP = (298.0, 452.0), (256.0, 246.0)
STAFF_X = 523.0
FIST_R = (STAFF_X, 398.0)
WL, WR = (262.0, 470.0), (500.0, 446.0)


def _on_stem(y):
    (x0, y0), (x1, y1) = PB_BASE, PB_TIP
    return (x0 + (x1 - x0) * (y - y0) / (y1 - y0), y)


def figure():
    sc = K.Scene(rank="Q")
    fc = K.face(HEAD, "3/4-right", sex="f", age="adult", lids="heavy", flick=2.5, mouth_hw=9.5, bow_rise=2.2,
                lip_hw=5.8, lip_sag=-2.4, lip_dy=45.0, brow_sag=4.6)
    # a queen's jaw: the kit egg with a smaller chin circle set a little lower
    # (eye-line geometry unchanged to 0.05 px; the jaw 2-3 px slimmer)
    hd, info = K.egg(HEAD, 42.0, chin_dx=0.12 * 84.0 * 0.55, chin_r=19.0, chin_dy=47.0)
    fc.head, fc.skin = hd, K.R(hd)
    side_x = lambda y: K._side_x(info, HEAD[0], HEAD[1], 42.0, y, +1)
    hl_far = [(396.0, 181.0), (410.0, 184.0)] + [(side_x(y) + 0.6, y) for y in (198.0, 214.0, 232.0, 248.0)] + \
             [(side_x(256.0) + 3.0, 258.0)]

    # ---- body, back to front ------------------------------------------------------
    sc.part("collar", K.standing_collar(NECK_X, top_y=234.0, half_w=102.0, neck_y=272.0, shoulder=(-122.0, 316.0),
                                        top_sag=8.0, side_sag=-5.0, rim=10.0, depth=60.0, color=K.JADE,
                                        rim_color=K.RED))
    cp = Q.cape(CAPE_L, CAPE_R, OPEN_L, OPEN_R)
    sc.part("cape", cp)
    hcap, hfall = H.queen_hair(
        fc, crown=(373.0, 206.0), r_near=58.0, r_far=51.0, near_low=(318.0, 240.0),
        hairline_near=((396.0, 181.0), (372.0, 185.0), (353.0, 193.0), (344.0, 210.0), (345.0, 232.0),
                       (352.0, 250.0), (358.0, 258.0)),
        far_outer=((412.0, 158.0), (428.0, 178.0), (437.0, 208.0), (436.0, 238.0), (427.0, 258.0)),
        hairline_far=hl_far,
        fall=((336.0, 226.0), (328.0, 262.0), (317.0, 298.0), (311.0, 334.0)), fall_w=(44.0, 30.0),
        n_cap=3, n_fall=4)
    sc.part("hair-fall", hfall)
    sc.part("neck", H.neck_chest(NECK_X))
    stom = Q.stomacher(386.0, top=356.0)
    gw = Q.gown(cp.meta["opening"], NECK_L, NECK_R, NECK_SAG, avoid=stom.shape.buffer(2.0),
                rows=[(236.0, 344.0, 504.0, 22.0, 12.0), (254.0, 344.0, 452.0, 22.0, 12.0),
                      (428.0, 470.0, 504.0, 22.0, 12.0), (428.0, 464.0, 452.0, 22.0, 12.0)])
    sc.part("gown", gw)
    sc.add("pearls", H.pearls((368.0, 279.0), (385.0, 293.0), (402.0, 279.0), d_min=5.2, d_max=8.4), None,
           sil=False)
    sc.part("stomacher", stom)
    sc.part("clasp", K.lion_clasp((386.0, 330.0), 40.0))

    # ---- head ------------------------------------------------------------------------
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("hair", hcap)
    sc.part("diadem", Q.portico(AXF, band_cx=380.0, band_top=175.0, band_h=10.0, band_hw=48.0, bow=8.0,
                                col_top=151.0, col_w=11.0, col_pitch=19.0, ent_h=7.0, ent_hw=40.0, ped_hw=44.0,
                                apex=119.0, oculus_r=6.5, mullions=True, studs=(340.0,),
                                acroterion=(11.0, 16.0)))

    # ---- arms and attributes -------------------------------------------------------------
    slL, cfL = K.sleeve(K.SleeveSpec(base=(206.0, 552.0), wrist=WL, sag=5.0, width=48.0, wrist_w=32.0, cuff=14.0,
                                     color=K.JADE, cuff_color=K.GOLD))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(514.0, 552.0), wrist=WR, sag=-4.0, width=46.0, wrist_w=32.0, cuff=14.0,
                                     color=K.JADE, cuff_color=K.GOLD))
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    bal = Q.balance(STAFF_X, half=64.0, beam_h=(14.0, 9.0), boss_r=7.0, staff_hw=9.0, pan_hw=17.0, pan_depth=12.0,
                    surf_ry=7.0, collars=(236.0, 300.0, 470.0))
    sc.part("staff", bal["staff"], halo=K.HALO, halo_only=("gown",))
    sc.part("beam", bal["beam"])
    sc.add("cords", bal["cords"].lines, None, sil=False)
    sc.part("panL", bal["panL"])
    sc.part("panR", bal["panR"])
    pb = Q.paintbrush(PB_BASE, PB_TIP, spike=70.0, tiers=((0.00, 46.0, 27.0, 13.5), (0.25, 34.0, 26.0, 13.0),
                                                           (0.48, 20.0, 22.0, 12.5)), top_len=0.34, dip=0.46)
    sc.part("paintbrush", pb, sil=False, halo=K.HALO, halo_only=("gown", "cape", "collar", "sleeveL"))
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    ang = math.degrees(math.atan2(PB_TIP[1] - PB_BASE[1], PB_TIP[0] - PB_BASE[0]))
    K.fist(_on_stem(424.0), ang, shaft_w=8.0, back=-1, wrist=WL, wrist_w=22.0, h=28.0, knuckle=9.5, reach=6.0,
           thumb_r=5.2).add_to(sc, "handL", halo=0.0)
    K.fist(FIST_R, -90.0, shaft_w=18.0, back=-1, wrist=WR, wrist_w=22.0, h=30.0, knuckle=10.0, reach=6.0,
           thumb_r=5.4).add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "Q")
    return sc


def build():
    return figure().layers()
