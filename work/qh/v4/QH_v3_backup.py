"""art/QH.py — Q♥ · The Aquamaid Queen (House of the Fount), brief §H.5.

(draft v3 — composition plan in progress)
"""
from __future__ import annotations

import numpy as np

from deck import courtkit as K
from deck.motifs import core as C

from art import _qh_attr as A
from art import _qh_body as B
from art import _qh_face as QF
from art import _qh_head as H

P = K.P
HEAD = (383.0, 204.0)


def figure():
    sc = K.Scene(rank="Q")
    fc = QF.queen_face(HEAD, wing_mode="hook", wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)

    # ---- behind everything: the air-hose ribbon from behind the far shoulder ----------
    rib = A.ribbon([(502, 338), (507, 302), (495, 262), (483, 222), (481, 188), (487, 162), (499, 148)], w=18.0)
    sc.part("hose", rib, sil=False)
    sc.add("bubbles", A.free_bubbles([((500, 133), 4.2), ((501, 118), 6.3), ((499, 99), 8.4),
                                      ((495, 77), 10.5)]), None, sil=False)

    # ---- the gown -------------------------------------------------------------------------
    gw = B.Gown(neck_l=(369, 298), neck_r=(406, 296),
                shoulder_l=[(318, 305), (266, 320)], shoulder_r=[(452, 302), (500, 316)],
                hole_l=[(282, 352), (296, 410), (304, 470), (308, 548)],
                hole_r=[(486, 350), (478, 410), (470, 470), (466, 548)],
                sweet=[(284, 376), (336, 350), (390, 370), (438, 348), (483, 374)],
                puff_l=None, puff_r=None,
                out_l=[(238, 305), (200, 316), (177, 344), (180, 384), (166, 450), (156, 548)],
                out_r=[(526, 304), (554, 315), (571, 342), (566, 384), (581, 450), (589, 548)])
    sc.part("sleeveL", gw.sleeve(-1))
    sc.part("sleeveR", gw.sleeve(+1))
    sc.part("torso", gw.torso(scale_r=10.0))
    sc.part("trim", B.pearls_on(gw.sweet_pts, d_max=8.4, d_min=6.3))
    sc.part("armletL", gw.armlet(-1, (180, 388), (293, 394), sag=-7.0, d=8.4))
    sc.part("armletR", gw.armlet(+1, (479, 392), (567, 388), sag=-6.0, d=8.4))

    # ---- hair (behind the head), neck, head, cap ---------------------------------------------
    sc.part("hairN", H.lock([(322, 178), (308, 222), (304, 262), (294, 292), (276, 308), (260, 302)], 56.0, n=6,
                            side=+1, bubbles=(4.2, 5.6, 7.0), bubble_lane=2, bubble_at=0.55))
    sc.part("hairF", H.lock([(436, 176), (446, 214), (449, 248), (448, 276), (458, 298), (472, 300)], 34.0, n=3,
                            side=-1))
    sc.part("neck", K.neck(fc, bottom=299.0, width=35.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    cap = H.PetalCap(c0=(390, 262), R0=84.0, h=13.0, dc=(378, 182), dR=72.0)
    sc.part("capbody", cap.body())
    sc.part("rim", cap.rim())
    a0 = cap.even(100.0 + 14.0, 5, squeeze=0.3)
    a1 = cap.even(128.0 + 10.0, 4, phase=0.5, squeeze=0.3)
    sc.part("cap0", cap.row(100.0, 0, 0, 0, angs=a0, length=30.0, shoulder=0.5, bulge=0.15))
    sc.part("cap1", cap.row(128.0, 0, 0, 0, angs=a1, length=28.0, bulge=0.15))
    sc.part("pearl", H.pearl((381, 108), 22.0, hl=4.2))

    # ---- pearl collar and the Lion Mark ---------------------------------------------------------
    for k, (y, sag, hw) in enumerate(((285.0, 5.0, 20.0), (297.5, 6.5, 22.0))):
        p0, p1 = P(388 - hw, y - 2), P(388 + hw, y - 3)
        pts = np.asarray(C.sample_d(K.arc_sag(p0, p1, -sag), 0.3)[0][0])
        sc.part(f"collar{k}", B.pearls_on(pts, d_max=7.6, d_min=6.4))
    sc.part("clasp", K.lion_clasp((390.0, 330.0), 40.0))

    # ---- the arrowhead sceptre ---------------------------------------------------------------------
    sc.part("stem", A.stem((546, 548), (546, 150), w=16.0, nodes=(0.55,)), halo=K.HALO,
            halo_only=("sleeveL", "sleeveR", "armletR"))
    sc.part("petiole", A.petiole((548, 330), (578, 274), w=9.0, sag=-8.0), sil=False)
    sc.part("leaf", A.arrow_leaf((578, 272), tilt=0.0, blade=74.0, half_w=22.0, lobe=(21.0, 36.0)))
    for nm, pt in A.flower((546, 124), r_petal=32.0, petal_w=34.0, centre_r=10.0):
        sc.part("flower-" + nm, pt)

    # ---- arms and hands ------------------------------------------------------------------------------
    faL = B.forearm((232, 532), (300, 452), width=50.0, wrist_w=34.0, sag=-3.0)
    faR = B.forearm((508, 532), (530, 474), width=46.0, wrist_w=30.0, sag=3.0)
    sc.part("armL", faL, halo=K.HALO, halo_only=("sleeveL", "sleeveR"))
    sc.part("armR", faR, halo=K.HALO, halo_only=("sleeveL", "sleeveR"))
    sc.part("braceletL", B.bracelet((300, 452), faL.meta["u"], 34.0, d=6.3))
    sc.part("braceletR", B.bracelet((530, 474), faR.meta["u"], 30.0, d=6.3))
    K.flat((304.0, 446.0), -30.0, side=-1, length=56.0, width=31.0).add_to(sc, "handL", halo=0.0)
    K.fist((546.0, 434.0), -90.0, shaft_w=16.0, back=-1, wrist=(530.0, 472.0), wrist_w=30.0, h=36.0).add_to(
        sc, "handR", halo=0.0)
    K.band_guard(sc, "Q")
    return sc


def build():
    return figure().layers()
