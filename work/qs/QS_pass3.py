"""art/QS.py — Q♠ · The Blind Oracle (creative brief §H.2). Pass 3."""
from __future__ import annotations

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from art import _qs_parts as Q
from art import _qs_face as QF
from art import _qs_body as B

P = K.P
HEAD = (386.0, 203.0)
TILT, PIVOT = -5.0, (384.0, 292.0)

# ---- head group (drawn upright, then inclined TILT about PIVOT) --------------------
VEIL = [(306, 330), (305, 290), (307, 245), (313, 205), (324, 172), (344, 148), (370, 136), (398, 133),
        (427, 138), (451, 154), (466, 180), (474, 225), (479, 290), (482, 330)]
OPENING = [(326, 330), (327, 262), (330, 222), (338, 194), (356, 182), (376, 178), (400, 180), (424, 188),
           (444, 204), (453, 240), (457, 300), (458, 330), (390, 420)]
VEIL_GUIDES = [
    ([(468, 176), (474, 218), (478, 262), (481, 320)], 1, -1, 0.0, 9.0),
    ([(318, 186), (310, 225), (307, 270), (306, 320)], 1, +1, 0.0, 9.0),
    ([(336, 156), (360, 140), (398, 134), (434, 141)], 1, -1, 0.0, 9.0),
]
CIRCLET = ((322.0, 165.0), (376.0, 167.0), (466.0, 153.0))
KITES = dict(xs=(335.0, 347.4, 360.4, 376.0, 392.2, 406.6, 420.6, 434.2, 447.2),
             lengths=(14.0, 17.0, 19.0, 30.0, 19.0, 17.5, 16.0, 14.5, 13.0),
             widths=(6.6, 7.2, 8.2, 10.0, 9.2, 8.6, 8.0, 7.4, 6.8), top_k=0.22)
LOCK_FAR = [(346, 186), (338, 225), (334, 270), (330, 318), (332, 368)]
LOCK_NEAR = [(432, 186), (444, 222), (450, 268), (455, 320), (458, 380)]

# ---- body (card frame) ------------------------------------------------------------
PLUMES = [  # root, tip, sag, feathered side, width   (back to front)
    ((356, 292), (296, 206), 10.0, -1, 36.0), ((410, 292), (470, 206), -10.0, +1, 36.0),
    ((350, 300), (254, 240), 10.0, -1, 38.0), ((416, 300), (512, 240), -10.0, +1, 38.0),
    ((346, 310), (228, 290), 8.0, -1, 36.0), ((420, 310), (538, 290), -8.0, +1, 36.0),
]
MANTLE = [(340, 300), (270, 312), (212, 326), (180, 352), (164, 410), (152, 480), (148, 540), (602, 540),
          (598, 480), (588, 410), (572, 352), (542, 326), (486, 312), (420, 300), (380, 296)]
GOWN = [(356, 294), (352, 360), (346, 440), (341, 540), (375, 556), (409, 540), (404, 440), (398, 360),
        (394, 294), (375, 288)]
LINING_L = [(360, 288), (328, 298), (316, 380), (304, 460), (294, 540), (318, 556), (343, 540), (348, 440),
            (354, 360)]
LINING_R = [(390, 288), (422, 298), (434, 380), (446, 460), (456, 540), (432, 556), (407, 540), (402, 440),
            (396, 360)]

MIRROR_C = (512.0, 362.0)
SAL = [(-31, -28), (-22, -19), (-8, -5), (4, 8), (10, 17), (12, 27), (6, 35), (-3, 38)]
SAL_K, SAL_D = 0.92, (6.0, -2.0)

WRIST_L, WRIST_R = (300.0, 470.0), (534.0, 490.0)
POSY = dict(mouth=(302.0, 392.0), axis_deg=-122.0)
FIST_L = (318.0, 424.0)
FIST_R = (512.0, 458.0)


def head_group():
    fc = QF.oracle_face(HEAD, eye_dy=12.0, mouth_dy=33.0, lip_dy=40.0, lip_sag=-1.4, lip_hw=4.6, brow_in=8.0)
    drape, crown = B.veil(VEIL, OPENING, guides=VEIL_GUIDES)
    diad = Q.stalactite_circlet(*CIRCLET, h=9.0, clip=drape.shape.buffer(-1.0), **KITES)
    lf = Q.hair_lock(LOCK_FAR, [(0.0, 26.0), (0.45, 28.0), (1.0, 22.0)], n_lines=2, stagger=10.0, line_from=0.0,
                     bias=-3.0)
    ln = Q.hair_lock(LOCK_NEAR, [(0.0, 30.0), (0.45, 34.0), (1.0, 26.0)], n_lines=3, stagger=10.0, line_from=0.0,
                     bias=3.0)
    hair = lf + ln
    head = K.Part(fc.skin, C.Frag(), fc.lines + K.outline(fc.head), {})
    neck = K.neck(fc, bottom=318.0, width=32.0)
    return fc, drape, crown, hair, head, neck, diad


def region(pts):
    return K.R(B.cspline(pts)).buffer(0)


def figure():
    sc = K.Scene(rank="Q")
    fc, drape, crown, hair, head, neck, diad = head_group()
    R_ = lambda p: Q.rot_part(p, TILT, PIVOT)                       # noqa: E731
    drape, crown, hair, head, neck, diad = [R_(p) for p in (drape, crown, hair, head, neck, diad)]

    # ---- body, back to front -------------------------------------------------------
    mreg = region(MANTLE)
    sc.part("veil", drape)
    sc.part("mantle", K.Part(mreg, K.fill(mreg, K.JADE), K.outline(mreg), {}))
    for i, (r0, t1, sg, sd, wd) in enumerate(PLUMES):
        sc.part(f"plume{i}", Q.plume(r0, t1, sag=sg, width=wd, n=5, side=sd, hatch=9.5, depth=3.0))
    for nm, pts in (("liningL", LINING_L), ("liningR", LINING_R)):
        rg = region(pts)
        sc.part(nm, K.Part(rg, K.fill(rg, K.RED), K.outline(rg), {}))
    gr = region(GOWN)
    sc.part("gown", K.Part(gr, C.Frag(), K.outline(gr), {}))
    sc.part("hair", hair)
    sc.part("neck", neck)
    sc.part("head", head)
    sc.part("veil-crown", crown)
    sc.part("diadem", diad)
    sc.part("brooch", K.lion_clasp((376.0, 320.0), 40.0))

    # ---- arms, attributes, hands ------------------------------------------------------
    slL, cfL = K.sleeve(K.SleeveSpec(base=(256.0, 552.0), wrist=WRIST_L, sag=6.0, width=50.0, wrist_w=32.0,
                                     cuff=14.0, color=K.JADE, cuff_color=K.RED))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(552.0, 552.0), wrist=WRIST_R, sag=-6.0, width=52.0, wrist_w=34.0,
                                     cuff=14.0, color=K.JADE, cuff_color=K.RED))
    sc.part("sleeveL", Q.drip_fringe_ko(slL, cfL))
    sc.part("sleeveR", Q.drip_fringe_ko(slR, cfR))
    sal_pts = [(MIRROR_C[0] + x * SAL_K + SAL_D[0], MIRROR_C[1] + y * SAL_K + SAL_D[1]) for x, y in SAL]
    mir = Q.mirror(MIRROR_C, 42.0, 57.5, handle_to=508.0, sal_pts=sal_pts)
    sc.part("mirror", mir, halo=K.HALO, halo_only=("mantle", "liningR", "plume5", "plume3", "hair"))
    posy = Q.laurel_posy(POSY["mouth"], POSY["axis_deg"], holder_len=44.0,
                         leaves=((-86.0, 58.0, 5.0), (-128.0, 62.0, -6.0), (-172.0, 54.0, 6.0)),
                         raceme=(118.0, 60.0, -5.0, 7, 6.4))
    sc.part("laurel", posy["leaves"], halo=K.HALO, halo_only=("mantle", "liningL", "plume4", "plume2", "hair"))
    sc.part("raceme", posy["raceme"], halo=K.HALO, halo_only=("mantle", "sleeveL", "liningL"))
    sc.part("holder", posy["holder"])
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    K.fist(FIST_L, POSY["axis_deg"], shaft_w=9.0, back=+1, wrist=WRIST_L, wrist_w=24.0, h=30.0).add_to(
        sc, "handL", halo=0.0)
    K.fist(FIST_R, -90.0, shaft_w=12.0, back=+1, wrist=WRIST_R, wrist_w=26.0, h=34.0).add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "Q")
    return sc


def build():
    return figure().layers()
