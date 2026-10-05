"""art/JH.py — J♥ · The Spring Minstrel (House of the Fount), creative brief §H.6.

Built with deck.courtkit (the K♠ hand) plus the minstrel's own parts in
art/_jh_parts.py and his profile in art/_jh_face.py.
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from art import _jh_face as JF
from art import _jh_parts as JP

P = K.P
HEAD = (392.0, 206.0)
FX = 530.0                                  # the fiddle's axis
BX = 262.0                                  # the bow stick's axis
SASH = ((268.0, 318.0), (375.0, 525.0))    # through the card centre: its 180° copy continues it


def figure():
    sc = K.Scene(rank="J")
    fc = JF.minstrel_profile(HEAD)

    # ---- the body ------------------------------------------------------------
    tunic_d, tunic = JP.spline_region([(206, 346), (232, 328), (290, 314), (340, 304), (370, 298), (398, 303),
                                       (424, 297), (468, 304), (522, 314), (560, 326), (584, 350), (590, 545),
                                       (200, 545)])
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)            # the neck runs down under the collar
    sc.part("tunic", K.Part(tunic, K.fill(tunic, K.RED), K.outline(tunic), {}))
    front_path = JP.open_spline([(404, 506), (402, 430), (398, 352)])[1]
    sc.add("piping-front", JP.bead_chain(front_path, grow=(5.4, 8.4), gap=4.6,
                                         keep=tunic.buffer(-3.5)), None, sil=False)
    sc.part("collar", JP.collar((368, 280), (424, 275), (366, 302), (428, 297), bot_sag=4.0))
    sc.part("clasp", K.lion_clasp((388.0, 330.0), 40.0))

    # ---- hair, beret, brooch, plume ------------------------------------------
    _, front = JP.spline_region([(406, 150), (409, 182), (419, 206), (422, 232), (428, 260), (500, 262), (500, 150)],
                                headings={0: 90.0, 5: -90.0, 6: 180.0})
    sc.part("hair", JP.lock_bundle([(432, 176), (458, 188), (473, 216), (477, 250), (470, 282)], n=4,
                                   ends=(1.0, 0.92, 0.84, 0.76), curl_deg=(120.0,),
                                   filler=fc.skin.intersection(front)))
    pl = JP.plume_locks([(436, 146), (446, 102), (476, 78), (522, 70), (560, 84), (574, 112)],
                        n=4, ends=(1.0, 0.80, 0.62, 0.45), curl_deg=120.0, curl_r=5.0)
    sc.part("plume", pl)
    sc.part("beret", JP.beret((402, 147), 88.0, 27.0, 15.0, -9.0, ((358, 182), (442, 190)), 13.0,
                              skull=fc.skin))
    sc.part("brooch", JP.fluke_heart((443.0, 140.0), u=21.0, bezel=3.4))

    # ---- the puffed sleeves, the sash over the left one ----------------------------
    sleeveL = JP.puff_sleeve([(314, 307), (262, 302), (208, 312), (172, 340), (157, 392), (160, 452), (182, 500),
                              (215, 522), (270, 524), (286, 470), (296, 410), (306, 356)],
                             [((228.0, 282.0), (44.0, 55.0, 69.3), 38.0, 142.0),
                              ((220.0, 366.0), (40.0, 51.0, 65.3), 36.0, 144.0),
                              ((218.0, 442.0), (32.0, 43.0, 57.3), 34.0, 146.0)])
    sc.part("sleeveL", sleeveL)
    sleeveR = JP.puff_sleeve([(444, 302), (502, 297), (552, 305), (588, 329), (604, 376), (607, 450), (606, 530),
                              (500, 530), (468, 470), (458, 400), (452, 346)],
                             [((528.0, 286.0), (42.0, 53.0, 67.3), 38.0, 142.0),
                              ((560.0, 366.0), (38.0, 49.0, 63.3), 36.0, 144.0),
                              ((566.0, 440.0), (30.0, 41.0, 55.3), 34.0, 146.0)])
    sc.part("sleeveR", sleeveR)
    sc.part("sash", JP.sash(SASH[0], SASH[1], 23.0, K.U(tunic, sleeveL.shape).buffer(-0.5)))

    # ---- the left forearm and the bow ----------------------------------------------
    WL = (246.0, 470.0)
    sl, cf = K.sleeve(K.SleeveSpec(base=(214.0, 545.0), wrist=WL, sag=-4.0, width=46.0, wrist_w=32.0,
                                   cuff=12.0, folds=0, color=K.JADE, cuff_color=K.RED))
    sc.part("forearmL", sl)
    sc.part("bow", JP.bow(BX, 112.0, 444.0, 490.0, color=K.GOLD, stick_w=7.4, hair_dx=15.0, camber=3.5),
            halo=K.HALO, halo_only=("sash", "sleeveL", "tunic"), sil=False)
    sc.part("cuffL", cf)
    K.fist((BX + 5.0, 424.0), -90.0, shaft_w=20.0, back=-1, wrist=WL, wrist_w=26.0,
           h=34.0).add_to(sc, "handL", halo=0.0)

    # ---- the right arm and the fiddle -------------------------------------------
    fd = JP.Fiddle(x=FX, body_top=296.0)
    sc.part("fiddle-neck", fd.neck_part())
    K.fist((FX, 281.0), -90.0, shaft_w=18.0, back=+1, wrist=(552.0, 330.0), wrist_w=26.0,
           h=34.0).add_to(sc, "handR", halo=0.0)
    sc.part("fiddle-body", fd.body_part())
    return sc


def build():
    return figure().layers()
