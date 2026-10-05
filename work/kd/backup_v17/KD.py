"""art/KD.py — K♦ · The Warden of the Ford (creative brief §H.10). WORK IN PROGRESS."""
from __future__ import annotations

import numpy as np
from shapely.geometry import Polygon

from deck import courtkit as K
from art import _kd_body as B
from art import _kd_crown as CR
from art import _kd_head as H

HEAD = (388.0, 208.0)
KEY_X = 552.0


def figure():
    sc = K.Scene(rank="K")
    fc = H.profile_face(HEAD)
    g = H.gold_mass(fc)

    # ---- body --------------------------------------------------------------
    ms = K.MantleSpec(neck_y=284.0, neck_heading=169.0, run=150.0, corner_r=30.0, side_heading=99.0)
    opening = K.R(K.Path((350.0, 292.0)).sag((426.0, 292.0), -10.0).sag((486.0, 545.0), 26.0)
                  .line((266.0, 545.0)).sag((350.0, 292.0), 26.0).close().d)
    tab_reg = opening.buffer(16.0, join_style=1).intersection(K.box(0, 284.0, 750, 545.0))
    sc.part("tabard", B.tabard(tab_reg, base_y=418.0, block=(52.0, 22.0), joint=2.9, heal=1.2))
    clasp_c = (381.0, 352.0)
    BL, WL = (222.0, 552.0), (300.0, 432.0)
    handL = K.flat(WL, -16.0, side=-1, length=52.0, width=29.0)
    avoid = K.U(K.box(clasp_c[0] - 20, clasp_c[1] - 20, clasp_c[0] + 20, clasp_c[1] + 20),
                handL.hand.shape, handL.thumb.shape)
    sc.part("sash", B.sash((352.0, 296.0), (482.0, 545.0), 52.0, tab_reg, rowel_r=16.0, pitch=60.0, first=68.0,
                           avoid=avoid))
    sc.part("mantle", B.open_mantle(ms, opening))

    # ---- head --------------------------------------------------------------
    skin = fc.skin.intersection(K.box(0.0, 0.0, 750.0, 296.0))
    sc.add("head", fc.lines + K.outline(skin), skin)
    sc.add("ear", H.ear_marks(g), None)
    sc.part("hair", H.hair(fc, g))
    mo = H.profile_moustache(fc)
    sc.part("beard", H.beard(fc, g))
    sc.part("moustache", mo)
    sc.part("crown", CR.dome_crown(CR.DomeSpec(ax=392.0, base=187.0)))
    sc.part("clasp", K.lion_clasp(clasp_c, 40.0))

    # ---- arms, key, hands --------------------------------------------------
    BR, WR = (505.0, 552.0), (528.0, 420.0)
    slL, _ = K.sleeve(K.SleeveSpec(base=BL, wrist=WL, sag=6.0, width=60.0, wrist_w=38.0, cuff=1.0, color=K.RED))
    slR, _ = K.sleeve(K.SleeveSpec(base=BR, wrist=WR, sag=-5.0, width=58.0, wrist_w=36.0, cuff=1.0, color=K.RED))
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    sc.part("key", B.key_of_ford(KEY_X, bow_c=(KEY_X, 124.0), ring_r=(40.0, 30.5), star_r=24.5, star_w=11.0, core_r=7.2,
                                     stem_hw=10.0, collar_hw=14.5, collars=(174.0, 250.0, 326.0)), halo=K.HALO, halo_only=("mantle",))
    uL = np.array(WL) - np.array(BL)
    uR = np.array(WR) - np.array(BR)
    sc.part("cuffL", B.gauntlet(WL, uL, width=40.0, flare=54.0, depth=38.0))
    sc.part("cuffR", B.gauntlet(WR, uR, width=38.0, flare=52.0, depth=38.0, mirror=True))
    handL.add_to(sc, "handL", halo=0.0)
    K.fist((KEY_X, 384.0), -90.0, shaft_w=20.0, back=-1, wrist=WR, wrist_w=28.0, h=38.0).add_to(sc, "handR",
                                                                                                  halo=0.0)
    K.band_guard(sc, "K")
    return sc


def build():
    return figure().layers()
