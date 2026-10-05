"""art/QC.py — Q♣ · The Wild-Rice Queen (House of the Reed), creative brief §H.8.

Built with deck.courtkit (the K♠'s hand) plus art/_qc_parts.py for the parts
the kit does not have (rice-spike coronet, wild-rice sceptre, egret plumes,
bertha, laced front, puffed sleeve caps, leaf textile).

Composition plan: filled in after the passes (see the table below).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K            # noqa: E402
from deck.motifs import core as C         # noqa: E402

import _qc_parts as Q                     # noqa: E402

AX = K.AX
HEAD = (386.0, 206.0)

# ---- body -----------------------------------------------------------------------
GOWN = dict(neck_c=(375.0, 332.0), neck=(338.0, 300.0), neck_sag=-9.0, shoulder=(222.0, 338.0), shoulder_sag=5.0,
            corner_r=34.0, hem=(196.0, 560.0))
LEAVES = dict(heading=56.0, length=170.0, width=16.0, row=50.0, step=214.0, origin=(375.0, 330.0), bend=(12.0, -12.0))
BERTHA = 30.0
PEARL = dict(d_end=6.3, d_mid=11.0, gap=5.5, margin=34.0)
LACE = dict(top=360.0, hw=(21.0, 15.0), rail=7.5, rung=7.0, pitch=24.0, first=18.0)
CLOAK = dict(top=(322.0, 270.0), shoulder=(168.0, 286.0), hem=(144.0, 560.0), corner_r=50.0, side_sag=-4.0)
PUFFS = ((236.0, 356.0), (514.0, 356.0))

# ---- head -----------------------------------------------------------------------
HAIRLINE = ((343.0, 214.0), (371.0, 180.0), (428.0, 205.0))
HAIR_L = dict(outer=[(380, 157), (350, 158), (330, 169), (318, 192), (315, 218), (318, 242), (313, 268), (302, 294),
                     (294, 322), (290, 352)],
              inner=[(380, 157), (372, 180), (356, 193), (352, 212), (356, 235), (364, 252), (370, 266), (370, 284),
                     (364, 310), (354, 336), (346, 352)],
              n=3)
HAIR_R = dict(outer=[(380, 157), (414, 157), (440, 167), (458, 190), (465, 218), (463, 244), (470, 270), (482, 296),
                     (490, 325), (494, 352)],
              inner=[(380, 157), (392, 178), (410, 190), (418, 210), (418, 232), (410, 250), (400, 263), (397, 285),
                     (404, 312), (414, 352)],
              n=3)
FACE = dict(lids="heavy", pupil_dx=3.0, mouth_hw=10.0, bow_rise=2.6, lip_hw=6.2, lip_dy=45.0)
FLICK = (5.0, -1.8)
NECK = ([(356, 236), (362, 262), (365, 285), (359, 312), (349, 336)],
        [(410, 236), (404, 262), (403, 285), (410, 312), (420, 336)])
BAND = dict(cx=385.0, top=163.0, h=13.0, hw=46.0, bow=5.0)
SPIKES = ((0.0, 0.0, 44.0, 12.6, 18.0),
          (-18.0, -7.0, 38.0, 10.6, 15.0), (18.0, 7.0, 38.0, 10.6, 15.0),
          (-34.0, -15.0, 31.0, 9.2, 12.0), (34.0, 15.0, 31.0, 9.2, 12.0))

# ---- attributes -------------------------------------------------------------------
SCEPTRE_X = 545.0
FIST_R = (545.0, 428.0)
# §G.5 on the sceptre: a tight spire of erect female spikelets (pairs, as the A♣'s stalk) over the
# spreading male branches with their hanging florets
SCEPTRE = dict(hw=9.5, knop_y=270.0, knop_hw=16.0, knop_h=12.0, nodes=(338.0, 478.0), node_hw=14.5, node_h=10.0,
               rachis_hw=3.8, rachis_top=156.0, terminal=(30.0, 10.0, 20.0),
               female=((214.0, 0, 7.0, 58.0, 27.0, 9.0, 18.0, 12.0), (184.0, 0, 7.0, 58.0, 27.0, 9.0, 18.0, 12.0)),
               arms=((256.0, 50.0, 8.0, 8.0, 6.5, ((0.40, 22.0, 8.0, 8.0), (0.70, 24.0, 8.2, 12.0),
                                                   (1.0, 25.0, 8.6, 16.0))),))
FIST_L = (316.0, 412.0)
FAN_AXIS = -118.0
# egret plumes, back to front: (heading, length, (bend1, bend2), w_max)
PLUMES = ((-158.0, 128.0, (-14.0, -52.0), 24.0), (-138.0, 150.0, (-18.0, -62.0), 25.0),
          (-118.0, 168.0, (-22.0, -70.0), 26.0), (-100.0, 180.0, (-26.0, -76.0), 26.0))


def head_group(sc):
    """head, hair locks (in front of the head, clipped round the face and
    below the coronet's top edge), coronet → the Face"""
    fc = K.face(HEAD, "3/4-left", sex="f", **FACE)
    a = fc.anchors
    s = a["spec"]
    # a lash flick on the NEAR eye only (the kit's ``flick`` would push the far
    # eye's corner through the cheek contour): one RULE tick rising outward
    oc = K.P(float(a["axis"]) + s.eye_dx + s.eye_w / 2, a["eye_y"])
    flick = K.seg(oc, oc + K.P(*FLICK), K.RULE, role="lid")
    sc.add("head", fc.lines + flick + K.outline(fc.head), fc.skin)
    zone = K.R(fc.head).intersection(K.R(K.arc3(*HAIRLINE) + "L520 600L240 600Z").buffer(0))
    band_reg, band_d = K.crown_band(**BAND)
    above = K.R(K.Path((200.0, 0.0)).line((BAND["cx"] - BAND["hw"], 0.0)).line(
        (BAND["cx"] - BAND["hw"], BAND["top"] - BAND["bow"])).arc3((BAND["cx"], BAND["top"]),
        (BAND["cx"] + BAND["hw"], BAND["top"] - BAND["bow"])).line((BAND["cx"] + BAND["hw"], 0.0)).line(
        (600.0, 0.0)).line((600.0, -50.0)).line((200.0, -50.0)).close().d)
    above = K.U(above, K.box(0, -100, 2000, BAND["top"] - BAND["bow"] - 0.5))
    for nm, spec in (("hairL", HAIR_L), ("hairR", HAIR_R)):
        lk = Q.hair_lock(fc, spec["outer"], spec["inner"], n=spec["n"], hairline=K.U(zone, above))
        sc.part(nm, lk)
    band, spikes = Q.coronet(fc, y=BAND["top"], h=BAND["h"], bow=BAND["bow"],
                             ends=(BAND["cx"] - BAND["hw"], BAND["cx"] + BAND["hw"]),
                             spikes=SPIKES, pedicel=9.0, jewel=10.5)
    sc.part("coronet-spikes", spikes, sil=False)
    sc.part("coronet", band)
    return fc


def head_scene():
    sc = K.Scene(rank="Q")
    sc.part("neck", Q.neck_chest(*NECK, bottom=360.0))
    fc = head_group(sc)
    return sc, fc


def fan_group(sc):
    import numpy as np
    u = np.array([np.cos(np.radians(FAN_AXIS)), np.sin(np.radians(FAN_AXIS))])
    f = np.array(FIST_L)
    top = f + u * 36.0
    root = top + u * 8.0
    for i, (hd, L, bend, wm) in enumerate(PLUMES):
        sc.part(f"plume{i}", Q.plume(tuple(root), hd, L, w_max=wm, bend=bend, n=3, split=0.42, peak=0.38,
                                     w_root=8.0, stagger=14.0))
    sc.part("handle", K.staff(tuple(f - u * 30.0), tuple(top), 12.0))
    # the ferrule: a reed node (§G.19 node ellipse) binding the plumes
    fer = K.R(C.ellipse_d(top[0], top[1], 13.0, 7.5, FAN_AXIS + 90.0))
    sc.part("ferrule", K.Part(fer, K.fill(fer, K.GOLD), K.outline(fer), {}))


def figure():
    sc = K.Scene(rank="Q")

    # ---- mantle (behind), neck, head, hair (the gown's neckline covers the hair's foot) ----
    sc.part("cloak", Q.cloak(**CLOAK))
    sc.part("neck", Q.neck_chest(*NECK, bottom=360.0))
    fc = head_group(sc)

    # ---- gown, bertha, lacing ---------------------------------------------------------
    gshape, top = Q.gown_outline(**GOWN)
    sc.part("gown", Q.gown(gshape, border=24.0, leaves=LEAVES))
    sc.part("bertha", Q.bertha(gshape, top, depth=BERTHA, pearl=PEARL))
    opening, ladder = Q.laced_front(**LACE)
    sc.part("opening", opening)
    sc.part("lacing", ladder)
    sc.part("brooch", K.lion_clasp((AX, 346.0), 40.0))
    for i, c in enumerate(PUFFS):
        sc.part(f"puff{i}", Q.puff(c, 32.0, rot=(18.0 if i == 0 else -18.0), slash_color=None))

    # ---- arms, attributes, hands --------------------------------------------------------
    WL, WR = (298.0, 452.0), (524.0, 470.0)
    slL, cfL = K.sleeve(K.SleeveSpec(base=(236.0, 560.0), wrist=WL, sag=5.0, width=48.0, wrist_w=34.0, cuff=14.0,
                                     color=K.RED, cuff_color=K.JADE))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(505.0, 560.0), wrist=WR, sag=-5.0, width=48.0, wrist_w=34.0, cuff=14.0,
                                     color=K.RED, cuff_color=K.JADE))
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    fan_group(sc)
    sp = Q.rice_sceptre(SCEPTRE_X, **SCEPTRE)
    sc.add("culm", C.Frag(), sp.meta["culm"], halo=K.HALO, halo_only=("gown",))     # the stalk joins the silhouette
    sc.add("sceptre", sp.frag, sp.shape, sil=False, halo=K.HALO, halo_only=("gown",))
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    K.fist(FIST_L, FAN_AXIS, shaft_w=10.0, back=-1, wrist=WL, wrist_w=26.0, h=32.0).add_to(sc, "handL", halo=0.0)
    K.fist(FIST_R, -90.0, shaft_w=19.0, back=-1, wrist=WR, wrist_w=26.0, h=34.0).add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "Q")
    return sc, fc


def build():
    sc, _ = figure()
    return sc.layers()
