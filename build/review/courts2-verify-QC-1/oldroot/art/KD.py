"""art/KD.py — K♦ · The Warden of the Ford (creative brief §H.10).

Strict profile left, the Dome Crown, the Key of the Ford upright in the axe
position (x 546, rowel-star bow at y 124), the left hand on the chest. Parts:
art/_kd_head.py (profile face, gold hair + squared beard), art/_kd_crown.py
(the Dome Crown), art/_kd_body.py (tabard, sash, key, gauntlets, mantle).

    tabard   red    plain Gill Red with a RUSTICATED HEM BAND (§G.20): a plinth
                    course 26 tall (the medallion sits in it, 7 px under its top
                    joint) and one course 20 tall of LONG blocks (3 px chamfers,
                    paper joints), under a cap rule (paper joint, 6 px red string,
                    paper joint) at y 450. Joints are placed where they fall in
                    the open or wholly under the arm / sash — a hem, not a wall
                    (director's note, final review).
    sash     jade   (352, 296) → (482, 545), 48 wide; gold rowels at 158 / 214,
                    Aquifer ford stones between; the Lion Mark as its buckle
    hands    paper  LEFT: the kit fist GRIPPING THE SASH'S LEFT EDGE just under the
                    buckle (grip 115 px down the sash, axis −100°, 14 px of
                    gathered edge; thumb over the index, 3 finger lines) —
                    a closed, working hand like the family's (director's note:
                    no open mitten). RIGHT: the kit fist on the key at y 384.
    arms     red    forearms from the band (222 / 500, 552); gold tooled-scroll
                    gauntlets (§G.31)
"""
from __future__ import annotations

import numpy as np
from shapely.geometry import Polygon

from deck import courtkit as K
from art import _kd_body as B
from art import _kd_crown as CR
from art import _kd_head as H

HEAD = (388.0, 211.0)
KEY_X = 546.0
SASH, SASH_W = ((352.0, 296.0), (482.0, 545.0)), 48.0
GRIP_T, GRIP_IN, GRIP_W = 115.0, 7.0, 14.0     # fist on the sash's left edge: distance down it, inset, gathered width
WRIST_OFF = np.array((-28.0, 30.0))            # wrist from the grip
FIST = dict(wrist_w=28.0, h=36.0, reach=6.0, knuckle=10.0)
GRIP_AXIS = -100.0                             # the fist's shaft axis (screen deg of its UP end); None = along the sash
# the rusticated hem: a plinth course 26 tall (the medallion sits in it, its
# joint 7 px clear) and one course 20 tall above, long blocks, bottom-up
HEM = ((26.0, (330.0, 450.0)), (20.0, (297.0, 390.0, 483.0)))
ROWELS = dict(first=158.0, pitch=56.0)


def figure():
    sc = K.Scene(rank="K")
    fc = H.profile_face(HEAD)
    g = H.gold_mass(fc, H.MassSpec(top_y=174.0, hair_foot=299.0, beard_foot=324.0))

    # ---- body --------------------------------------------------------------
    ms = K.MantleSpec(neck_y=284.0, neck_heading=171.5, run=150.0, corner_r=30.0, side_heading=99.0)
    opening = K.R(K.Path((347.0, 292.0)).sag((429.0, 292.0), -10.0).sag((493.0, 545.0), 26.0)
                  .line((259.0, 545.0)).sag((347.0, 292.0), 26.0).close().d)
    tab_reg = opening.buffer(16.0, join_style=1).intersection(K.box(0, 284.0, 750, 545.0))
    sc.part("tabard", B.tabard(tab_reg, HEM, joint=3.0, chamfer=3.0, cap=(3.0, 6.0)))
    clasp_c = (381.0, 352.0)
    # the left hand GRIPS THE SASH'S EDGE (the kit fist, the sash's edge gathered
    # in it as the shaft; its axis tilted −100° so the finger block lies level
    # like the key hand's, the wrist down-left toward the band)
    su = (np.array(SASH[1]) - np.array(SASH[0])) / np.hypot(*(np.array(SASH[1]) - np.array(SASH[0])))
    sn = np.array([su[1], -su[0]])
    grip = np.array(SASH[0]) + su * GRIP_T - sn * (SASH_W / 2 - GRIP_IN)
    BL = (222.0, 552.0)
    WL = tuple(grip + WRIST_OFF)
    axis = float(np.degrees(np.arctan2(-su[1], -su[0]))) if GRIP_AXIS is None else GRIP_AXIS
    handL = K.fist(tuple(grip), axis, shaft_w=GRIP_W, back=-1, wrist=WL, **FIST)
    avoid = K.U(K.box(clasp_c[0] - 20, clasp_c[1] - 20, clasp_c[0] + 20, clasp_c[1] + 20),
                handL.hand.shape, handL.thumb.shape)
    sc.part("sash", B.sash(SASH[0], SASH[1], SASH_W, tab_reg, rowel_r=16.5, avoid=avoid, **ROWELS))
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
                                                dome_h=40.0, lantern_h=9.0, cap_r=9.5, finial_d=11.5,
                                                rib_span=30.0)))
    sc.part("clasp", K.lion_clasp(clasp_c, 40.0))

    # ---- arms, key, hands --------------------------------------------------
    BR, WR = (500.0, 552.0), (522.0, 420.0)
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
    K.fist((KEY_X, 384.0), -90.0, shaft_w=22.0, back=-1, wrist=WR, wrist_w=28.0, h=38.0).add_to(sc, "handR",
                                                                                                  halo=0.0)
    K.band_guard(sc, "K")
    return sc


def build():
    return figure().layers()
