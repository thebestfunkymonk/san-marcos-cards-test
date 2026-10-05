"""art/JC.py — J♣ · The River Squire (House of the Reed), creative brief §H.9.

Built with deck.courtkit (the K♠'s hand) plus art/_jc_face.py (the 3/4-left
face), art/_jc_head.py (hair, heron plume), art/_jc_body.py (jerkin, sleeves,
pecan work), art/_jc_paddle.py (the paddle) and art/_jc_parts.py (cap, husk).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K  # noqa: E402
from deck.motifs import core as C  # noqa: E402
from deck.motifs import geometric as MG  # noqa: E402
import _jc_body as B  # noqa: E402
import _jc_face as F  # noqa: E402
import _jc_head as H  # noqa: E402
import _jc_paddle as PD  # noqa: E402
import _jc_parts as J  # noqa: E402

HEAD = (385.0, 207.0)
PADDLE_X = 548.0
FIST = (548.0, 408.0)
WL, WR = (272.0, 436.0), (524.0, 440.0)
BELT_Y = 440.0
LEAF = dict(length=68.0, pairs=3, leaflet=(19.0, 4.8), angle=55.0, step=12.0, first=9.0, falcate=0.7, bend=2.5)


def figure():
    sc = K.Scene(rank="J")
    fc = F.face34(HEAD, bow_rise=0.8, bow_sag=-0.5, chin_r=18.0, chin_dy=50.0, mouth_dy=40.0, lip_dy=47.5,
                  brow_dy=-12.0, brow_sag=2.6, far_brow_sag=2.0, mouth_hw=9.5)

    # ---- body, back to front ----------------------------------------------------
    torso = B.region([(342, 301), (300, 310), (266, 322), (244, 340)],
                     [(244, 340), (246, 420), (244, 530)], ("L", [(244, 530), (536, 530)]),
                     [(536, 530), (538, 420), (536, 340)],
                     [(536, 340), (512, 322), (466, 308), (418, 300)], ("L", [(418, 300), (342, 301)]))
    e_l = [(334, 302), (338, 350), (358, BELT_Y - 4.0)]
    e_r = [(410, 300), (390, 360), (358, BELT_Y - 4.0)]
    s_l = [(358, BELT_Y + 8.0), (345, 490), (330, 530)]
    s_r = [(358, BELT_Y + 8.0), (372, 490), (388, 530)]
    v_top = B.region(e_l, e_r[::-1], ("L", [(410, 300), (334, 302)]))
    v_bot = B.region(s_l, ("L", [(330, 530), (388, 530)]), s_r[::-1])
    vee = K.U(v_top, v_bot)
    sc.add("doublet", K.fill(torso, K.JADE) + K.outline(torso), torso)
    jer = torso.difference(vee)
    bl = J.belt(torso, y=BELT_Y, h=20.0, sag=4.0, x0=220.0, x1=560.0, front=358.0)
    g_parts = [B.ladder_guard(e_l, 15.0, side=-1, extend=(8.0, 0.0), clip=jer),
               B.ladder_guard(e_r, 15.0, side=+1, extend=(8.0, 0.0), clip=jer),
               B.ladder_guard(s_l, 14.0, side=+1, extend=(0.0, 8.0), clip=jer, node_every=0),
               B.ladder_guard(s_r, 14.0, side=-1, extend=(0.0, 8.0), clip=jer, node_every=0)]
    guards = K.U(*[g.shape for g in g_parts])
    field = jer.difference(bl.shape.buffer(3.0)).difference(guards.buffer(3.0))
    lf_l, nut_l = B.pecan_field(field.intersection(K.box(0, 0, 358, 2000)), origin=(292.0, 372.0), heading=-116.0,
                                pitch=(44.0, 40.0), leaf_kw=LEAF)
    lf_r, nut_r = B.pecan_field(field.intersection(K.box(358, 0, 2000, 2000)), origin=(440.0, 372.0), heading=-64.0,
                                pitch=(44.0, 40.0), leaf_kw=LEAF)
    sc.add("jerkin", K.fill(C.knockout(K.D(jer), lf_l + lf_r, nut_l.select(lambda m: m.kind == "fill"),
                                       nut_r.select(lambda m: m.kind == "fill")), K.RED) + K.outline(jer), jer)
    sc.add("nuts", nut_l + nut_r, None, sil=False)
    for k, g in enumerate(g_parts):
        sc.part(f"guard{k}", g)
    sc.part("belt", bl)
    # puffed sleeve heads: the far (left) arm akimbo, the near (right) arm hanging
    arm_l = B.region([(262, 326), (228, 330), (200, 352), (188, 392), (184, 440)],
                     ("L", [(184, 440), (240, 452)]), [(240, 452), (246, 420), (252, 370), (262, 326)])
    sc.part("armL", B.sleeve_part(arm_l, ["M224 350L202 436"]))
    arm_r = B.region([(512, 318), (554, 324), (584, 350), (594, 392), (590, 450), (584, 530)],
                     ("L", [(584, 530), (534, 530)]), [(534, 530), (540, 440), (532, 370), (512, 318)])
    sc.part("armR", B.sleeve_part(arm_r, ["M566 350L576 505"]))

    # ---- head -------------------------------------------------------------------
    sc.part("hair", H.hair_locks(
        back=[(450, 166), (478, 184), (490, 214), (490, 248)],
        scallops=[(490, 248), (480, 268), (463, 280), (444, 284)],
        front=[(426, 274), (426, 220), (430, 176)],
        strand_guides=[[(472, 176), (482, 208), (482, 242), (478, 258)],
                       [(460, 184), (468, 218), (466, 254), (460, 270)],
                       [(447, 194), (452, 232), (447, 264), (440, 276)]],
        sag=9.0, curl_deg=120.0, curl_r=3.6))
    sc.part("neck", K.neck(fc, bottom=312.0, width=40.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("collar", B.falling_collar())
    sc.part("ear", J.ear(fc))
    vane, quill = H.heron_plume2([(458, 152), (462, 126), (480, 104), (510, 90), (546, 84), (578, 76), (598, 74)],
                                 w_max=30.0, w_root=12.0, n=3, curl_side=1, vane_from=24.0, quill=36.0, quill_w=8.0)
    sc.part("plume", vane)
    sc.part("quill", quill)
    sc.part("cap", J.cap(fc, tip=(292.0, 171.0), top=(393.0, 106.0), flap_tip=(473.0, 130.0), hatband=10.5))
    sc.part("clasp", K.lion_clasp((370.0, 336.0), 40.0))
    sc.part("buckle", J.pecan_husk((358.0, BELT_Y + 4.0), style="D", s=1.15))
    for k, y in enumerate((372.0, 400.0)):
        x = 370.0 - (y - 336.0) * 12.0 / 100.0
        c = K.circle((x, y), 6.3)
        sc.add(f"button{k}", K.fill(c, K.GOLD) + K.outline(c, K.FINE), K.R(c).buffer(K.FINE / 2), sil=False)

    # ---- arms, paddle, hands -------------------------------------------------------
    fl = B.region([(204, 434), (274, 419)], ("L", [(274, 419), (274, 453)]),
                  [(274, 453), (220, 480), (196, 482), (180, 466), (182, 446), (204, 434)])
    sc.part("forearmL", B.sleeve_part(fl, ["M202 458L256 440"]))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(490.0, 552.0), wrist=WR, sag=-6.0, width=50.0, wrist_w=34.0, cuff=12.0,
                                     color=K.JADE, cuff_color=K.RED))
    sc.part("sleeveR", slR)
    sc.part("paddle", PD.paddle(PADDLE_X, tip=106.0), halo=K.HALO, halo_only=("jerkin", "armR", "doublet"))
    sc.part("cuffR", cfR)
    sc.part("cuffL", B.cuff((262.0, 422.0), (263.0, 452.0), 12.0))
    K.flat((WL[0] + 2.0, WL[1]), -2.0, side=-1, length=50.0, width=29.0).add_to(sc, "handL", halo=0.0)
    K.fist(FIST, -90.0, shaft_w=20.0, back=-1, wrist=WR, wrist_w=26.0, h=36.0).add_to(sc, "handR", halo=0.0)
    return sc


def build():
    return figure().layers()
