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
    sash     jade   (352, 296) → (482, 545), 52 wide; gold rowels at 158 / 214,
                    Aquifer ford stones between; the Lion Mark as its buckle
    hands    paper  LEFT: the kit fist (h 38, as the key hand) GRIPPING THE SASH'S
                    LEFT EDGE just under the buckle (grip 115 px down the sash,
                    axis −106°, 10 px of gathered edge; thumb over the index, 3
                    finger lines) — a closed, working hand like the family's
                    (director's note: no open mitten). The edge is pulled out to
                    the fist above it and HELD through it: it comes out from
                    under the little finger and eases back, so the cloth runs
                    through the fist like a shaft. RIGHT: the kit fist on the key
                    at y 384, from the body side (palm view).
    arms     red    forearms from the band (222 / 492, 552); gold gauntlets, ONE
                    unit of tooled scroll each (§G.31), both lying level
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
SASH, SASH_W = ((352.0, 296.0), (482.0, 545.0)), 52.0
CLASP_S, CLASP_N = 63.0, -2.25                   # the Lion Mark on the sash: s along it, offset across (+n = right)
GRIP_T, GRIP_IN, GRIP_W = 109.0, -4.0, 10.0    # fist on the sash's left edge: distance down it, inset (− = out past it), gathered width
FIST = dict(wrist_w=24.0, h=38.0, reach=6.0, knuckle=10.0)
GRIP_AXIS = -106.0                             # the fist's shaft axis (screen deg of its UP end); None = along the sash
# the sash's edge PULLED OUT to the fist (depth < 0: toward the knuckles, easing in over ``span`` above), its
# apex GATHER_DS along the sash from the grip; the pull HOLDS through the fist so the gathered edge comes out
# from under the little finger (a jade tongue between the heel and the fingertips — the cloth runs through
# the fist like a shaft) and then eases back over ``span_lo``; no crease lines (they read as whiskers)
GATHER = dict(depth=-13.0, span=46.0, hold=30.0, span_lo=36.0, creases=[])
GATHER_DS = -8.0                               # (the apex under the thumb: the edge dives in under it, not at its tip)
FINGER_ENDS_L = {2: 0.40, 3: 0.46}
ARM_L_BASE = (240.0, 552.0)                    # the sash arm's forearm leaves the band here
WRIST_L = dict(bend=30.0, dist=0.62)           # the sash hand's wrist: out along its axis (kit fist_wrist); short: a compact fist
KEY_FIST = dict(shaft_w=22.0, back=-1, h=38.0)
# the rusticated hem: a plinth course 26 tall (the medallion sits in it, its
# joint 7 px clear) and one course 20 tall above, long blocks, bottom-up
HEM = ((26.0, (354.0, 450.0)), (20.0, (297.0, 390.0, 483.0)))
ROWELS = dict(first=158.0, pitch=56.0)
OPEN_TR = 421.0     # the tabard opening's top-right corner, under the hair (no red sliver between hair and mantle)
OPEN_SAG_L = 34.0  # its left edge's bow (26 → 34: the red chest a little fuller — red 11.9 → 12.4 % after the
                   # sash widened to 52 for the Lion Mark, §C.2 12–16)
OPEN_SAG = 23.0    # its right edge's bow: it runs in under the key gauntlet's LEFT SIDE half-way down (at 26 it ran
                   # into the cuff's top corner — a tangency; at ≤ 22 into its bottom corner)
# the key arm: forearm from the band, wrist out along the fist's axis (kit fist_wrist)
# (base, sag and width keep the forearm's left edge ≥ 4 px clear of the sash's second rowel;
# clear_x/y: the plain strip of mantle between the forearm and the key, below the gauntlet)
ARM_R = dict(base=(505.0, 552.0), sag=-2.0, width=74.0, wrist_w=40.0, bend=50.0, dist=0.85, shift=4.0,
             clear_x=495.0, clear_y=425.0)
# gold gauntlets, ONE unit of §G.31 tooled scroll each (the J♦ cuff sprig: stem, eye volute, sessile leaf)
SPRIG = dict(r0=8.4, q=6.0, flat=2.0, leaf=(12.6, 5.0), pet=0.9, free=True)
# (the left cuff sits on a 45° forearm: its unit is turned −40° so it lies level like the right one's —
# drawn across that arm it stood on end and read as a letter S — and drawn a size smaller to fit the turn)
CUFF_L = dict(width=36.0, flare=46.0, depth=34.0, sprig_rot=-40.0,
              sprig=dict(SPRIG, r0=7.8, q=5.6, flat=2.8, leaf=(11.5, 5.0), x_first=4.5, yc=3.0))
CUFF_R = dict(width=40.0, flare=48.0, depth=34.0, sprig=dict(SPRIG, x_first=5.0, yc=4.0))

CUFF_R = dict(CUFF_R, sprig=dict(SPRIG, x_first=2.0, yc=4.0))


def figure():
    sc = K.Scene(rank="K")
    fc = H.profile_face(HEAD)
    g = H.gold_mass(fc, H.MassSpec(top_y=174.0, hair_foot=299.0, beard_foot=324.0))

    # ---- body --------------------------------------------------------------
    ms = K.MantleSpec(neck_y=284.0, neck_heading=171.5, run=150.0, corner_r=30.0, side_heading=99.0)
    opening = K.R(K.Path((347.0, 292.0)).sag((OPEN_TR, 292.0), -10.0).sag((493.0, 545.0), OPEN_SAG)
                  .line((259.0, 545.0)).sag((347.0, 292.0), OPEN_SAG_L).close().d)
    tab_reg = opening.buffer(16.0, join_style=1).intersection(K.box(0, 284.0, 750, 545.0))
    tab = B.tabard(tab_reg, HEM, joint=3.0, chamfer=3.0, cap=(3.0, 6.0))
    # its top-right corner ends wholly under the hair / shoulder contour junction: the RED PLATE there is cut
    # (a crumb the contour would hide — QA 4c) but the shape is kept, so the silhouette corner is unchanged
    tab = K.Part(tab.shape, K.clip_out(tab.fills, K.box(439.0, 280.0, 452.0, 300.5), trap=0.0), tab.lines, tab.meta)
    sc.part("tabard", tab)
    su = (np.array(SASH[1]) - np.array(SASH[0])) / np.hypot(*(np.array(SASH[1]) - np.array(SASH[0])))
    sn = np.array([su[1], -su[0]])
    clasp_c = tuple(np.array(SASH[0]) + su * CLASP_S + sn * CLASP_N)
    # the left hand GRIPS THE SASH'S EDGE: the kit fist closed on the edge (the
    # "shaft"), the edge pulled out to it in a tent (GATHER), the finger block
    # near level like the key hand's, the wrist down-left toward the band
    grip = np.array(SASH[0]) + su * GRIP_T - sn * (SASH_W / 2 - GRIP_IN)
    BL = ARM_L_BASE
    axis = float(np.degrees(np.arctan2(-su[1], -su[0]))) if GRIP_AXIS is None else GRIP_AXIS
    fkw = dict(shaft_w=GRIP_W, back=-1, h=FIST["h"], reach=FIST["reach"], knuckle=FIST["knuckle"])
    WL = tuple(K.fist_wrist(tuple(grip), axis, **WRIST_L, **fkw))     # out along the hand's axis
    handL = K.fist(tuple(grip), axis, wrist=WL, wrist_w=FIST["wrist_w"], **fkw)
    handL = B.refine_fist(handL, tuple(grip), axis, fkw=fkw, line_ends=FINGER_ENDS_L)
    avoid = K.U(K.box(clasp_c[0] - 20, clasp_c[1] - 20, clasp_c[0] + 20, clasp_c[1] + 20),
                handL.hand.shape, handL.thumb.shape)
    # the key hand (the king's LEFT, from the body side: palm view), its wrist out along its axis
    WR = tuple(K.fist_wrist((KEY_X, 384.0), -90.0, bend=ARM_R["bend"], dist=ARM_R["dist"], **KEY_FIST))
    handR = K.fist((KEY_X, 384.0), -90.0, wrist=WR, wrist_w=26.0, hand="L", **KEY_FIST)
    handR = B.refine_fist(handR, (KEY_X, 384.0), -90.0, fkw=KEY_FIST)
    # the forearms and gauntlets (stacked later; built now so the ornament behind can keep clear)
    BR = ARM_R["base"]
    slL, _ = K.sleeve(K.SleeveSpec(base=BL, wrist=WL, sag=6.0, width=64.0, wrist_w=38.0, cuff=1.0, color=K.RED))
    # the key arm runs on BEHIND the key (the palm is behind the shaft, so the forearm is too): its
    # sleeve and gauntlet reach in under the shaft and the key's paper halo cuts them — no strip of
    # mantle is left between the forearm and the key, no paper tab under the heel. The gauntlet
    # stands ``shift`` px toward the key from the wrist (the wrist in its left part, the right part
    # under the halo), and the sleeve's end is the gauntlet's.
    ur = (np.array(WR) - np.array(BR)) / np.hypot(*(np.array(WR) - np.array(BR)))
    WRc = tuple(np.array(WR) - np.array([ur[1], -ur[0]]) * ARM_R["shift"])
    slR, _ = K.sleeve(K.SleeveSpec(base=BR, wrist=WRc, sag=ARM_R["sag"], width=ARM_R["width"],
                                   wrist_w=ARM_R["wrist_w"], cuff=1.0, color=K.RED))
    cuffL = B.gauntlet(WL, np.array(WL) - np.array(BL), **CUFF_L)
    key_cut = K.box(0, 0, 750, 750).difference(
        K.box(KEY_X - 11.0, 0, KEY_X + 11.0, 750).buffer(K.HALO + K.MEDIUM / 2 + K.MEDIUM / 2))
    cuffR = B.gauntlet(WRc, np.array(WRc) - np.array(BR), mirror=True, keep_in=key_cut, **CUFF_R)
    arms = K.U(slL.shape, slR.shape, cuffL.shape, cuffR.shape)
    key = B.key_of_ford(KEY_X, bow_c=(KEY_X, 124.0), ring_r=(40.0, 30.0), star_r=22.2, star_w=10.5, core_r=7.5,
                        stem_hw=11.0, collar_hw=15.5, collars=(174.0, 250.0, 326.0), bit_out=(38.0, 25.0),
                        stones=(212.0, 288.0), ward=(454.0, 6.8, 14.0))
    sc.part("sash", B.sash(SASH[0], SASH[1], SASH_W, tab_reg, rowel_r=16.5, avoid=avoid,
                           gather=dict(GATHER, s=GRIP_T + GATHER_DS), **ROWELS))
    # the mantle's chain stones stand whole or not at all beside the arms and the key hand;
    # below the right gauntlet the strip between the forearm and the key is left plain
    # (its chain rules would run 0–3 px alongside the sleeve's edge)
    sc.part("mantle", B.open_mantle(ms, opening, avoid=K.U(handR.hand.shape.buffer(K.HALO + K.MEDIUM / 2 + 1.0), arms,
                                                          key.shape.buffer(K.HALO + K.CONTOUR / 2)),
                                    clear=K.box(ARM_R["clear_x"], ARM_R["clear_y"], KEY_X, 560.0)))

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
                                                rib_span=30.0, stone=(10.0, 4.8), stone_span=32.0, stone_dy=0.3,
                                                hatch_shift=3.5)))   # one aligned hatch set: no line grazes a gore's top corner (QA 12)
    sc.part("clasp", K.lion_clasp(clasp_c, 40.0))

    # ---- arms, key, hands --------------------------------------------------
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    sc.part("cuffR", cuffR)
    sc.part("key", key, halo=K.HALO, halo_only=("mantle", "sleeveR", "cuffR"))
    sc.part("cuffL", cuffL)
    handL.add_to(sc, "handL", halo=0.0)
    handR.add_to(sc, "handR", halo=0.0)
    for nm in ("handL", "handR"):
        B.trim_behind(sc, nm)          # lines running in under a hand end inside its outline (no cap nubs)
    K.band_guard(sc, "K")
    return sc


def build():
    return figure().layers()
