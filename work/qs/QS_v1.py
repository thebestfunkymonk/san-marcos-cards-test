"""art/QS.py — Q♠ · The Blind Oracle (creative brief §H.2), built with deck.courtkit
and the Q♠ parts in art/_qs_parts.py, art/_qs_face.py. (Draft.)
"""
from __future__ import annotations

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from inkkit import geom as G
from art import _qs_parts as Q
from art import _qs_face as QF

P = K.P
HEAD = (385.0, 208.0)
TILT, PIVOT = -4.0, (385.0, 300.0)          # the head inclines toward her gaze: listening
MIRROR_C = (510.0, 352.0)

# head group (upright frame; inclined by TILT about PIVOT)
VEIL_FAR = [(292, 336), (300, 278), (309, 226), (322, 182), (346, 152)]
VEIL_APEX = (384, 138)
VEIL_NEAR = [(424, 146), (455, 170), (473, 214), (485, 270), (495, 336)]
EDGE_FAR = [(356, 183), (338, 194), (327, 218), (322, 248), (318, 282), (314, 318)]
EDGE_NEAR = [(410, 183), (429, 194), (442, 220), (450, 250), (456, 284), (462, 318)]
VEIL_CUT_Y = 246.0                           # the veil crown (in front of the hair) ends here
BAND = ((330, 170), (375, 177), (446, 168))
PLUMES = [  # root, tip, sag, feathered side
    ((360, 276), (286, 222), -8.0, +1), ((402, 276), (478, 220), 8.0, -1),
    ((352, 290), (250, 262), -8.0, +1), ((410, 290), (518, 258), 8.0, -1),
    ((350, 304), (236, 312), -6.0, +1), ((412, 304), (534, 308), 6.0, -1),
]
SAL = [(-31, -28), (-22, -19), (-8, -5), (4, 8), (10, 17), (12, 27), (6, 35), (-3, 38)]


def head_group(fc):
    """veil (back, crown), hair, neck, head, diadem — upright."""
    _, pf, _ = __import__("deck.motifs.forms", fromlist=["arc_spline"]).arc_spline(EDGE_FAR)
    _, pn, _ = __import__("deck.motifs.forms", fromlist=["arc_spline"]).arc_spline(EDGE_NEAR)
    top = np.vstack([pf[::-1], pn])                       # far foot → over the brow → near foot
    opening = Polygon(np.vstack([top, [[top[-1][0], 360], [top[0][0], 360]]])).buffer(0)
    veil_back, veil_crown = Q.veil(VEIL_FAR, VEIL_APEX, VEIL_NEAR, opening, apex_in=-24.0, apex_out=24.0)
    crown = veil_crown.shape.intersection(K.box(0, 0, 750, VEIL_CUT_Y))
    crown_lines = K.clip_in(veil_crown.lines, crown.buffer(0.5))
    veil_crown = K.Part(crown, veil_crown.fills, crown_lines, veil_crown.meta)
    hair = Q.hair_under_veil([tuple(p) for p in top[::6]], 312.0, n=2, face=fc.skin)
    neck = K.neck(fc, bottom=330.0, width=34.0)
    head = K.Part(fc.skin, C.Frag(), fc.lines + K.outline(fc.head), {})
    diad = Q.stalactite_diadem(*BAND, h=8.0, lengths=(21.0, 9.0), widths=(10.0, 5.0))
    return veil_back, veil_crown, hair, neck, head, diad


def figure():
    sc = K.Scene(rank="Q")
    fc = QF.oracle_face(HEAD, brow_dy=-17.0)
    R_ = lambda p: Q.rot_part(p, TILT, PIVOT)                       # noqa: E731
    veil_back, veil_crown, hair, neck, head, diad = [R_(p) for p in head_group(fc)]

    # ---- body -----------------------------------------------------------------------
    outer = K.R(K.spline([(158, 548), (166, 440), (182, 372), (206, 346), (248, 326), (300, 310), (340, 300),
                          (380, 296), (420, 298), (470, 306), (524, 322), (556, 342), (574, 380), (588, 450),
                          (596, 548)], closed=True))
    opening = K.R(K.spline([(352, 290), (340, 360), (328, 440), (316, 548), (438, 548), (428, 440), (418, 360),
                            (406, 290)], closed=True))
    g_reg = opening.buffer(4)
    g_lines = K.outline(g_reg)
    edge_pts = C.sample_d(K.spline([(352, 300), (340, 360), (328, 440), (316, 548)]), 0.5)[0][0]
    g_lines += K.current_lines(edge_pts, 3, opening, side=-1, first=26.0, pitch=14.0, edge=K.MEDIUM, stagger=22.0)
    seam = C.sample_d(K.spline([(398, 318), (408, 380), (416, 440), (424, 520)]), 0.5)[0][0]
    scv = G.Curve(seam)
    for s in np.arange(0.0, scv.length, 11.0):
        g_lines += K.dot(scv.at_s(s), 4.2, role="seam-dot")
    gown = K.Part(g_reg, C.Frag(), g_lines, {})
    mant_reg = outer.difference(opening)
    mantle = K.Part(mant_reg, K.fill(mant_reg, K.JADE), K.outline(mant_reg), {})
    lap_reg = mant_reg.intersection(opening.buffer(22.0))
    lapels = K.Part(lap_reg, K.fill(lap_reg, K.RED), K.outline(lap_reg), {})

    sc.part("veil-back", veil_back)
    sc.part("mantle", mantle)
    sc.part("lapels", lapels)
    sc.part("hair", hair)
    for i, (r0, t1, sg, sd) in enumerate(PLUMES):
        sc.part(f"plume{i}", Q.gill_plume_lobe(r0, t1, sag=sg, width=30.0, n=6, side=sd))
    sc.part("neck", neck)
    sc.part("gown", gown)
    sc.part("brooch", K.lion_clasp((372.0, 322.0), 40.0))
    sc.part("head", head)
    sc.part("veil-crown", veil_crown)
    sc.part("diadem", diad)

    # ---- arms, attributes, hands ------------------------------------------------------
    WL, WR = (300.0, 456.0), (532.0, 488.0)
    slL, cfL = K.sleeve(K.SleeveSpec(base=(258.0, 552.0), wrist=WL, sag=6.0, width=50.0, wrist_w=32.0, cuff=14.0,
                                     color=K.JADE, cuff_color=K.RED))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(552.0, 552.0), wrist=WR, sag=-6.0, width=52.0, wrist_w=34.0, cuff=14.0,
                                     color=K.JADE, cuff_color=K.RED))
    slL = Q.drip_fringe_ko(slL, cfL)
    slR = Q.drip_fringe_ko(slR, cfR)
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    sal_pts = [(MIRROR_C[0] + x, MIRROR_C[1] + y) for x, y in SAL]
    mir = Q.mirror(MIRROR_C, 47.0, 58.0, handle_to=508.0, sal_pts=sal_pts)
    sc.part("mirror", mir, halo=K.HALO, halo_only=("mantle", "lapels", "plume4", "plume5", "plume3"))
    lau = Q.laurel_sprig((318, 432), (284, 372),
                         leaves_spec=[dict(base=(284, 372), heading=-140.0, length=66.0, bend=-6.0),
                                      dict(base=(284, 372), heading=-100.0, length=54.0, bend=5.0, n_pairs=2),
                                      dict(base=(284, 372), heading=178.0, length=52.0, bend=6.0, n_pairs=2)],
                         raceme_top=(272, 382), raceme_len=62.0, raceme_bend=5.0, raceme_heading=96.0,
                         n_florets=7, floret_r=6.5)
    sc.part("stem", lau["stem"])
    sc.part("laurel", lau["leaves"], halo=K.HALO, halo_only=("mantle", "lapels", "gown"))
    sc.part("raceme", lau["raceme"], halo=K.HALO, halo_only=("mantle", "sleeveL", "laurel"), sil=False)
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    K.fist((316.0, 424.0), -118.0, shaft_w=10.0, back=+1, wrist=WL, wrist_w=24.0, h=32.0).add_to(sc, "handL", halo=0.0)
    K.fist((510.0, 460.0), -90.0, shaft_w=12.0, back=+1, wrist=WR, wrist_w=26.0, h=34.0).add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "Q")
    return sc


def build():
    return figure().layers()
