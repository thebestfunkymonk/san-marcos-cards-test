"""art/JH.py — J♥ · The Spring Minstrel (House of the Fount), creative brief §H.6.

Built with deck.courtkit (the K♠ hand) plus the minstrel's own parts in
art/_jh_parts.py and his profile in art/_jh_face.py. Draft pass 3.
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from art import _jh_face as JF
from art import _jh_parts as JP

P = K.P
HEAD = (388.0, 206.0)
FIDDLE_X = 516.0
BOW_X = 266.0
SASH = ((298.0, 312.0), (375.0, 525.0))


def figure():
    sc = K.Scene(rank="J")
    fc = JF.profile_left(HEAD, JF.ProfileSpec(r=43.0))

    # ---- body --------------------------------------------------------------
    tunic_pts = [(192, 340), (222, 326), (262, 318), (310, 312), (352, 304), (374, 297), (400, 301), (426, 296),
                 (470, 308), (520, 318), (560, 330), (584, 350), (588, 540), (192, 540)]
    _, tunic = JP.spline_region(tunic_pts)
    tunic = tunic.intersection(K.box(188, 0, 750, 600))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)          # the neck runs down under the tunic
    sc.part("tunic", K.Part(tunic, K.fill(tunic, K.RED), K.outline(tunic), {}))
    neck_path = JP.open_spline([(348, 313), (374, 305), (400, 309), (428, 303), (456, 311)])[1]
    sc.add("piping-neck", JP.bead_chain(neck_path, d=8.4, gap=3.4), None, sil=False)
    front_path = JP.open_spline([(394, 506), (388, 430), (380, 360)])[1]
    sc.add("piping-front", JP.bead_chain(front_path, gap=4.4, grow=(5.0, 9.0)), None, sil=False)
    sc.part("sash", JP.sash(SASH[0], SASH[1], 21.0, tunic.buffer(-0.5)))
    sc.part("clasp", K.lion_clasp((374.0, 334.0), 40.0))

    # ---- hair, beret, brooch, plume ------------------------------------------
    sc.part("hair", JP.hair_bob([(406, 196), (452, 202), (468, 230), (468, 264), (456, 288), (434, 295),
                                 (416, 284), (410, 256), (408, 226)],
                                [(426, 178), (460, 206), (466, 250), (450, 290)], n=4, side=-1))
    sc.part("beret", JP.beret([(350, 193), (336, 184), (318, 170), (326, 150), (370, 134), (428, 132),
                               (468, 146), (476, 166), (466, 184), (450, 202), (400, 196)],
                              rim=((318, 172), (400, 180), (474, 168)), button=(404.0, 134.0)))
    pl = JP.plume((372.0, 182.0), -82.0, [(120, -55), (64, -60), (38, -60), (26, -40)], hw_max=21.0, belly=0.42,
                  stagger=12.0, locks=6, lock_depth=6.5, n=3, lock_from=0.22, root_hw=5.0, side=+1)
    sc.part("plume", pl)
    sc.part("brooch", JP.fluke_heart((372.0, 185.0), u=21.0, bezel=3.5))

    # ---- the left arm and the bow ----------------------------------------------
    arm_d, arm = JP.spline_region([(168, 384), (176, 346), (204, 328), (240, 322), (262, 342), (266, 392),
                                   (256, 452), (240, 496), (198, 512), (172, 470)])
    sl_f = JP.ripple_slashes(None, (214.0, 300.0), (40.0, 51.0, 65.3), 38.0, 142.0)
    sl_f += JP.ripple_slashes(None, (214.0, 392.0), (26.0, 37.0, 51.3), 30.0, 150.0)
    sl_f = K.clip_in(sl_f, arm.buffer(-(K.CONTOUR / 2 + 3.2 + K.MEDIUM / 2)))
    arm_fill = C.knockout(K.D(arm), sl_f)
    sc.part("armL", K.Part(arm, K.fill(arm_fill, K.JADE), K.outline(arm), {}))
    sl, cf = K.sleeve(K.SleeveSpec(base=(205.0, 540.0), wrist=(248.0, 466.0), sag=-4.0, width=46.0, wrist_w=32.0,
                                   cuff=12.0, folds=0, color=K.JADE, cuff_color=K.RED))
    sc.part("forearmL", sl)
    bw = JP.bow(BOW_X, 176.0, 446.0, 505.0, color=K.JADE)
    sc.part("bow", bw, halo=K.HALO)
    sc.part("cuffL", cf)
    K.fist((BOW_X + 6.0, 424.0), -90.0, shaft_w=24.0, back=-1, wrist=(248.0, 466.0), wrist_w=26.0,
           h=34.0).add_to(sc, "handL", halo=0.0)

    # ---- the fiddle -------------------------------------------------------------
    armR_d, armR = JP.spline_region([(520, 336), (556, 328), (586, 342), (600, 380), (604, 450), (604, 540),
                                     (548, 540), (540, 420)])
    slR = JP.ripple_slashes(None, (566.0, 312.0), (40.0, 51.0, 65.3), 38.0, 142.0)
    slR = K.clip_in(slR, armR.buffer(-(K.CONTOUR / 2 + 3.2 + K.MEDIUM / 2)))
    sc.part("armR", K.Part(armR, K.fill(C.knockout(K.D(armR), slR), K.JADE), K.outline(armR), {}))
    fd = JP.Fiddle(x=FIDDLE_X, scroll_c=(FIDDLE_X, 166.0), nut=246.0, body_top=335.0, fb_end=408.0, bridge=438.0,
                   tail_top=456.0)
    sc.part("fiddle-neck", fd.neck_part())
    K.fist((FIDDLE_X, 294.0), -90.0, shaft_w=22.0, back=+1, wrist=(562.0, 330.0), wrist_w=26.0,
           h=34.0).add_to(sc, "handR", halo=0.0)
    sc.part("fiddle-body", fd.body_part())
    return sc


def build():
    return figure().layers()
