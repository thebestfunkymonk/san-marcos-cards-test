"""art/KD.py — K♦ · The Warden of the Ford (creative brief §H.10). WORK IN PROGRESS."""
from __future__ import annotations

import numpy as np
from shapely.geometry import Polygon

from deck import courtkit as K
from art import _kd_body as B
from art import _kd_crown as CR
from art import _kd_head as H

HEAD = (388.0, 211.0)
KEY_X = 552.0


def figure():
    sc = K.Scene(rank="K")
    fc = H.profile_face(HEAD)
    g = H.gold_mass(fc, H.MassSpec(top_y=174.0, hair_foot=299.0, beard_foot=324.0))

    # ---- body --------------------------------------------------------------
    ms = K.MantleSpec(neck_y=284.0, neck_heading=170.5, run=150.0, corner_r=30.0, side_heading=99.0)
    opening = K.R(K.Path((347.0, 292.0)).sag((429.0, 292.0), -10.0).sag((493.0, 545.0), 26.0)
                  .line((259.0, 545.0)).sag((347.0, 292.0), 26.0).close().d)
    tab_reg = opening.buffer(16.0, join_style=1).intersection(K.box(0, 284.0, 750, 545.0))
    sc.part("tabard", B.tabard(tab_reg, base_y=430.0, block=(52.0, 22.0), joint=2.9, heal=1.2))
    clasp_c = (381.0, 352.0)
    BL, WL = (222.0, 552.0), (314.0, 444.0)
    handL = K.flat(WL, -12.0, side=-1, length=52.0, width=29.0)
    avoid = K.U(K.box(clasp_c[0] - 20, clasp_c[1] - 20, clasp_c[0] + 20, clasp_c[1] + 20),
                handL.hand.shape, handL.thumb.shape)
    sc.part("sash", B.sash((352.0, 296.0), (482.0, 545.0), 52.0, tab_reg, rowel_r=17.5, pitch=60.0, first=68.0,
                           avoid=avoid))
    sc.part("mantle", B.open_mantle(ms, opening))

    # ---- head --------------------------------------------------------------
    skin = fc.skin.intersection(K.box(0.0, 0.0, 750.0, 299.0))
    sc.add("head", fc.lines + K.outline(skin), skin)
    sc.add("ear", H.ear_marks(g), None)
    sc.part("hair", H.hair(fc, g, n=4))
    mo = H.profile_moustache(fc)
    sc.part("beard", H.beard(fc, g))
    sc.part("moustache", mo)
    sc.part("crown", CR.dome_crown(CR.DomeSpec(ax=394.0, base=186.0, circlet_h=15.0, drum_h=21.0, cornice_h=6.5,
                                                dome_h=42.0, lantern_h=10.0, cap_r=10.0, finial_d=12.0,
                                                rib_span=30.0)))
    sc.part("clasp", K.lion_clasp(clasp_c, 40.0))

    # ---- arms, key, hands --------------------------------------------------
    BR, WR = (505.0, 552.0), (528.0, 420.0)
    slL, _ = K.sleeve(K.SleeveSpec(base=BL, wrist=WL, sag=6.0, width=64.0, wrist_w=38.0, cuff=1.0, color=K.RED))
    slR, _ = K.sleeve(K.SleeveSpec(base=BR, wrist=WR, sag=-5.0, width=62.0, wrist_w=36.0, cuff=1.0, color=K.RED))
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    sc.part("key", B.key_of_ford(KEY_X, bow_c=(KEY_X, 124.0), ring_r=(40.0, 30.0), star_r=22.2, star_w=10.5, core_r=7.5,
                                     stem_hw=11.0, collar_hw=15.5, collars=(174.0, 250.0, 326.0), bit_out=(38.0, 25.0),
                                 stones=(212.0, 288.0), ward=(454.0, 6.8, 14.0)), halo=K.HALO, halo_only=("mantle",))
    uL = np.array(WL) - np.array(BL)
    uR = np.array(WR) - np.array(BR)
    sc.part("cuffL", B.gauntlet_scroll(WL, uL, width=42.0, flare=60.0, depth=44.0, height=28.0))
    sc.part("cuffR", B.gauntlet_scroll(WR, uR, width=40.0, flare=58.0, depth=44.0, height=28.0, mirror=True))
    handL.add_to(sc, "handL", halo=0.0)
    K.fist((KEY_X, 384.0), -90.0, shaft_w=20.0, back=-1, wrist=WR, wrist_w=28.0, h=38.0).add_to(sc, "handR",
                                                                                                  halo=0.0)
    K.band_guard(sc, "K")
    return sc


def build():
    return figure().layers()
