"""art/QH.py — Q♥ · The Aquamaid Queen (House of the Fount), brief §H.5.

(draft v3 — composition plan in progress)
"""
from __future__ import annotations

import numpy as np

from deck import courtkit as K
from deck.motifs import core as C

from art import _qh_attr as A
from art import _qh_body as B
from art import _qh_cap as CP
from art import _qh_face as QF
from art import _qh_head as H
from art import _qh_hand as HD

P = K.P
HEAD = (383.0, 204.0)
CAP_C, CAP_R = (377.0, 192.0), 66.0
HOSE = [(505, 338), (500, 300), (489, 262), (481, 228), (482, 200), (490, 184), (500, 176)]
BUBBLES = [(502, 166), (494, 142), (486, 116), (484, 90), (488, 64)]
HAIR_N = [(320, 190), (302, 226), (292, 262), (278, 290), (252, 305), (228, 302), (214, 290)]
PETAL_ROWS = (dict(u0=0.62, u1=0.0, n=5, phase=0.5, widen=1.2),      # top row (behind), tips up to the pearl
              dict(u0=0.90, u1=0.28, n=6, phase=0.0, widen=1.15),
              dict(u0=1.02, u1=0.56, n=7, phase=0.5, widen=1.1))      # front row, roots under the rim


def figure():
    sc = K.Scene(rank="Q")
    fc = QF.queen_face(HEAD, wing_mode="hook", wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)

    # ---- behind everything: the air hose from behind the far shoulder --------------------
    hp, fer = A.hose(HOSE, w0=11.0, w1=14.0, bub=None, ferrule=9.0)
    sc.part("hose", hp, sil=False)
    sc.part("ferrule", fer, sil=False)
    sc.add("bubbles", A.bubble_rise(BUBBLES, d0=4.2, ratio=1.22, gap0=5.0, d_max=10.5), None, sil=False)

    # ---- the gown -------------------------------------------------------------------------
    gw = B.Gown(neck_l=(369, 298), neck_r=(406, 296),
                shoulder_l=[(318, 305), (266, 320)], shoulder_r=[(452, 302), (500, 316)],
                hole_l=[(278, 352), (286, 410), (292, 470), (294, 548)],
                hole_r=[(488, 350), (484, 410), (480, 470), (478, 548)],
                sweet=[(284, 376), (336, 350), (390, 370), (438, 348), (483, 374)],
                puff_l=None, puff_r=None,
                out_l=[(236, 303), (190, 310), (163, 336), (157, 366), (168, 392), (158, 450), (148, 548)],
                out_r=[(528, 302), (566, 310), (590, 336), (594, 366), (583, 392), (594, 450), (602, 548)])
    sc.part("sleeveL", gw.sleeve(-1, border=17.0, pitch=12.0))
    sc.part("sleeveR", gw.sleeve(+1, border=17.0, pitch=12.0))
    sc.part("torso", gw.torso(scale_r=15.0))
    sc.part("trim", B.pearls_on(gw.sweet_pts, d_max=9.5, d_min=6.3))
    sc.part("armletL", gw.armlet(-1, (168, 388), (290, 394), sag=-7.0, d=9.5))
    sc.part("armletR", gw.armlet(+1, (482, 392), (588, 388), sag=-6.0, d=9.5))

    # ---- hair (behind the head), neck, head, cap ---------------------------------------------
    sc.part("hairN", H.lock(HAIR_N, 54.0, n=5, taper=0.42, taper_from=0.45,
                            side=+1, bubbles=(4.2, 5.6, 7.0), bubble_lane=2, bubble_at=0.55))
    sc.part("hairF", H.lock([(432, 188), (444, 218), (448, 250), (447, 278), (458, 300), (476, 304)], 38.0, n=4,
                            side=-1))
    sc.part("neck", K.neck(fc, bottom=299.0, width=35.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    cap = CP.Cap(CAP_C, CAP_R, yaw=24, pitch=16, tilt=10, t_front=68.5, t_back=112, t_side=100, rim_h=11)
    sc.part("capbase", cap.base())
    for k, rw in enumerate(PETAL_ROWS):
        for phi, pt in cap.petals(**rw, lift=0.14, tip="round", shoulder=0.5, rib=False):
            sc.part(f"petal{k}_{phi:.0f}", pt)
    sc.part("rim", cap.rim())
    sc.part("pearl", cap.pearl(d=16.0, r=1.1))

    # ---- pearl collar and the Lion Mark ---------------------------------------------------------
    for k, (y, sag, hw) in enumerate(((285.0, 5.0, 20.0), (297.5, 6.5, 22.0))):
        p0, p1 = P(388 - hw, y - 2), P(388 + hw, y - 3)
        pts = np.asarray(C.sample_d(K.arc_sag(p0, p1, -sag), 0.3)[0][0])
        sc.part(f"collar{k}", B.pearls_on(pts, d_max=7.6, d_min=6.4))
    sc.part("clasp", K.lion_clasp((390.0, 330.0), 40.0))

    # ---- the arrowhead sceptre ---------------------------------------------------------------------
    sc.part("stem", A.stem((546, 548), (546, 116), w=19.0, nodes=(0.53, 0.84)), halo=K.HALO,
            halo_only=("sleeveL", "sleeveR", "armletR"))
    sc.part("petiole", A.petiole((550, 322), (574, 284), w=9.0, sag=-6.0), sil=False)
    sc.part("leaf", A.arrow_leaf2((574, 282), tilt=4.0, blade=86.0, half_w=23.0, lobe=(21.0, 38.0)))
    for nm, pt in A.flower3((546, 112), r_petal=50.0, petal_w=40.0, centre_r=12.5, squash=0.78, tilt=-10.0,
                            notch=5.0, centre="scallop", hatch_rel=0.0):
        sc.part("flower-" + nm, pt)

    # ---- arms and hands ------------------------------------------------------------------------------
    faL = B.forearm((232, 532), (300, 452), width=50.0, wrist_w=34.0, sag=-3.0)
    faR = B.forearm((508, 532), (530, 474), width=46.0, wrist_w=30.0, sag=3.0)
    sc.part("armL", faL, halo=K.HALO, halo_only=("sleeveL", "sleeveR"))
    sc.part("armR", faR, halo=K.HALO, halo_only=("sleeveL", "sleeveR"))
    sc.part("braceletL", B.bracelet((300, 452), faL.meta["u"], 34.0, d=6.3))
    sc.part("braceletR", B.bracelet((530, 474), faR.meta["u"], 30.0, d=6.3))
    HD.lady_hand((303.0, 450.0), -24.0, length=66.0, width=31.0, wrist_w=24.0, side=-1, tips=(5.0, 0.0, 3.0, 10.0),
                 thumb=(0.12, 0.5), thumb_out=5.0, knuckle=0.45, vgap=3.6).add_to(
        sc, "handL", halo=K.HALO, halo_only=("torso", "trim"))
    K.fist((546.0, 434.0), -90.0, shaft_w=19.0, back=-1, wrist=(530.0, 472.0), wrist_w=30.0, h=36.0).add_to(
        sc, "handR", halo=0.0)
    K.band_guard(sc, "Q")
    return sc


def build():
    return figure().layers()
