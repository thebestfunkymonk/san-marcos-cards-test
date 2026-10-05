"""art/QC.py — Q♣ · The Wild-Rice Queen (House of the Reed), creative brief §H.8.

Built with deck.courtkit (the K♠'s hand) plus art/_qc_parts.py for the
parts the kit does not have (rice-spike coronet, wild-rice sceptre, egret
plumes, reed-ladder lacing, gown, puffs, leaf textile).

Composition plan: see the module docstring table, filled in after the passes.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K            # noqa: E402
from deck.motifs import core as C         # noqa: E402

import _qc_parts as Q                     # noqa: E402

AX = K.AX
HEAD = (385.0, 207.0)
SCEPTRE_X = 545.0
FIST_R = (545.0, 428.0)
SCEPTRE = dict(arm=(34.0, 13.0, 5.0), florets=((0.5, 24.0, 8.0, 3.0), (1.0, 26.0, 8.7, 6.0)))
CLOAK = dict(top=(300.0, 316.0), shoulder=(192.0, 326.0), hem=(146.0, 560.0))
GOWN = dict(neck_y=312.0, neck_x=322.0, neck_top=296.0, shoulder=(214.0, 336.0), corner_r=30.0, hem_x=196.0)
LEAVES = dict(heading=60.0, length=220.0, width=22.0, row=62.0, step=250.0, bend=(10.0, -10.0))
LACED = dict(top_y=318.0, top_hw=36.0, tip_y=488.0, rail=8.5, bar=9.0, pitch=22.0, first=28.0)


CORONET = ((0.0, 0.0, 46.0, 15.4, 6.0, 18.0),
           (-17.0, -15.0, 40.0, 13.4, 6.0, 15.0), (17.0, 15.0, 40.0, 13.4, 6.0, 15.0),
           (-31.0, -30.0, 31.0, 10.4, 6.0, 12.0), (31.0, 30.0, 31.0, 10.4, 6.0, 12.0))
CORONET_Y, CORONET_ENDS = 167.0, (350.0, 421.0)
HAIRLINE = ((343.0, 214.0), (372.0, 181.0), (428.0, 206.0))
HAIR_L = dict(outer=[(379, 155), (352, 162), (334, 182), (324, 216), (322, 256), (312, 296), (320, 336), (338, 370)],
              inner=[(379, 155), (372, 181), (356, 200), (362, 250), (369, 292), (356, 336), (338, 370)], n=4,
              starts=[None, 262, 280, 296], ends=[0, 8, 16, 24])
HAIR_R = dict(outer=[(379, 155), (410, 158), (436, 172), (453, 197), (464, 230), (466, 264), (455, 300), (469, 338),
                     (474, 370), (456, 398)],
              inner=[(379, 155), (372, 181), (400, 190), (414, 215), (408, 250), (397, 282), (398, 304), (422, 342),
                     (440, 374), (456, 398)], n=5, starts=[None, None, 214, 250, 290], ends=[0, 8, 16, 24, 32])


# egret plumes: (outer spline, inner spline) root → tip, a fountain arching up and drooping outward
PLUMES = (
    dict(outer=[(292, 366), (292, 312), (286, 258), (268, 216), (236, 196), (206, 202), (190, 226), (188, 252)],
         inner=[(278, 370), (278, 318), (272, 274), (258, 246), (238, 234), (220, 238), (212, 252), (212, 266)], n=3),
    dict(outer=[(290, 366), (270, 312), (246, 270), (212, 248), (178, 252), (158, 278), (154, 306)],
         inner=[(276, 372), (258, 328), (240, 298), (218, 284), (196, 286), (182, 300), (178, 316)], n=3),
    dict(outer=[(288, 368), (258, 334), (222, 320), (188, 324), (164, 344), (156, 370)],
         inner=[(274, 376), (248, 358), (220, 350), (198, 354), (182, 366), (178, 380)], n=3),
)


def fan_group(sc):
    """the egret-plume fan: plumes (paper, current lines) arching from a gold ferrule on a gold handle"""
    for i, spec in enumerate(PLUMES):
        sc.part(f"plume{i}", Q.hair_lock(None, spec["outer"], spec["inner"], n=spec["n"], face_clip=False,
                                         color=None, stagger=10.0))
    sc.part("handle", K.staff((310.0, 448.0), (284.0, 382.0), 11.0))
    fer = K.rrect(269.0, 371.0, 297.0, 384.0, 3.2)
    sc.part("ferrule", K.Part(K.R(fer), K.fill(fer, K.GOLD), K.outline(fer), {}))


def head_group(sc):
    """head, hair locks (in front of the head, clipped round the face), coronet → the Face"""
    fc = K.face(HEAD, "3/4-left", sex="f", lids="heavy", pupil_dx=2.5, flick=3.0)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    hl = K.arc3(*HAIRLINE)
    zone = K.R(fc.head).intersection(K.R(hl + "L520 600L240 600Z").buffer(0))
    for nm, spec in (("hairL", HAIR_L), ("hairR", HAIR_R)):
        sc.part(nm, Q.hair_lock(fc, spec["outer"], spec["inner"], n=spec["n"], hairline=zone,
                                starts=spec.get("starts"), ends=spec.get("ends")))
    hair = K.U(*[it.occ for it in sc.items if it.name in ("hairL", "hairR")])
    band, spikes = Q.coronet(fc, y=CORONET_Y, h=10.0, bow=5.0, spikes=CORONET, studs=(-10.0, 10.0, -26.0, 26.0),
                             ends=CORONET_ENDS, hair=hair)
    sc.part("coronet-spikes", spikes, sil=False)
    sc.part("coronet", band, sil=False)
    return fc


def figure():
    sc = K.Scene(rank="Q")

    # ---- cloak (behind), neck, gown ---------------------------------------------------
    sc.part("cloak", Q.cloak(**CLOAK))
    sc.part("neck", Q.neck_chest([(365, 250), (363, 282), (352, 306), (336, 322)],
                                 [(399, 250), (402, 282), (412, 306), (428, 322)]))
    gshape, gm = Q.gown_outline(**GOWN)
    inner = gshape.buffer(-24.0, quad_segs=16)
    leaves = Q.leaf_field(inner, **LEAVES)
    gown = K.Part(gshape, K.fill(gshape, K.JADE),
                  K.outline(gshape) + C.stroke(K.D(inner), K.FINE, role="seam") + leaves, {})
    sc.part("gown", gown)
    lining, ladder = Q.laced_v(gshape, gm["N"], gm["S0"], **LACED)
    sc.part("lining", lining)
    sc.part("lacing", ladder)

    # ---- head, hair, coronet ------------------------------------------------------
    fc = head_group(sc)
    sc.part("brooch", K.lion_clasp((AX + 2.0, 324.0), 40.0))

    # ---- arms, attributes, hands ------------------------------------------------
    WL, WR = (282.0, 462.0), (524.0, 474.0)
    slL, cfL = K.sleeve(K.SleeveSpec(base=(238.0, 552.0), wrist=WL, sag=5.0, width=42.0, wrist_w=58.0, cuff=18.0,
                                     color=K.JADE, cuff_color=K.RED))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(505.0, 552.0), wrist=WR, sag=-5.0, width=42.0, wrist_w=58.0, cuff=18.0,
                                     color=K.JADE, cuff_color=K.RED))
    sc.part("sleeveL", slL, halo=K.HALO, halo_only=("gown",))
    sc.part("sleeveR", slR, halo=K.HALO, halo_only=("gown",))
    fan_group(sc)
    sp = Q.rice_finial_sceptre(SCEPTRE_X, **SCEPTRE)
    sc.add("culm", C.Frag(), sp.meta["culm"], halo=K.HALO, halo_only=("gown",))    # the culm joins the silhouette
    sc.add("sceptre", sp.frag, sp.shape, sil=False)
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    K.fist((297.2, 416.0), -111.8, shaft_w=11.0, back=-1, wrist=WL, wrist_w=26.0, h=34.0).add_to(sc, "handL", halo=0.0)
    K.fist(FIST_R, -90.0, shaft_w=14.0, back=-1, wrist=WR, wrist_w=26.0, h=36.0).add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "Q")
    return sc, fc


def build():
    sc, _ = figure()
    return sc.layers()
