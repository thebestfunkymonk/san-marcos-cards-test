"""art/JH.py — J♥ · The Spring Minstrel (House of the Fount), creative brief §H.6.

Built with deck.courtkit (the K♠ hand) plus the minstrel's own parts:
art/_jh_face.py (his profile), art/_jh_head.py (beret, plume, bob),
art/_jh_parts.py (fiddle, bow, sash, piping, sleeves) and art/_jh_hands.py
(how the kit fists meet the neck, the frog and the arms).

Composition plan (top half, card px; the system adds clip, 180° copy, frame,
♥ ripple band, pips and indices):

| part        | colour | geometry |
|-------------|--------|----------|
| head        | paper  | strict profile LEFT (one-eyed), r 42.5 about (386, 208); eye y 214, chin ≈ 269, under-chin ≈ 275 (tilted −5° about the throat) |
| face        | ink    | 9 strokes: RULE lid lowered to the front, Ø6 pupil tucked under it, brow, nostril, mouth (upper-lip bow) + FINE lower-lip tick, ear C, MEDIUM jaw from under the chin to under the ear |
| neck        | paper  | the throat turns down under the chin; ≈ 14 px of neck front drops into the collar |
| hair        | gold   | page-boy bob behind the ear, rolled under at the nape, 4 current lines |
| beret       | jade   | soft disc tilted back, lip over the brow (328, 174), crown 110, drooping to (510, 186) behind; band 15 tall with gold bead piping |
| plume       | gold   | one long plume laid across the beret from the brooch (398, 162) to (586, 96), 4 current lines, tip rolled into a volute |
| brooch      | red    | fluke heart u 17.5 (a pip) in a 3 px paper channel knocked out of a 6.2 px gold bezel with a MEDIUM contour (the pin of the plume) |
| collar      | jade   | standing collar, top 289 at the throat rising to 276 under the bob, foot ≈ 304–312; gold beads |
| tunic       | red    | shoulders ≈ 300–330 to the band; gold bubble-chain piping down the front; paper bubbles knocked out |
| clasp       | gold   | Lion Mark 40 px at (388, 333.5), clear of the collar's foot |
| sleeves     | jade   | puffed upper sleeves, slashed with ripple arcs (paper) |
| sash        | paper  | 46 wide, (268, 318) → the card centre (continues across the band in the 180° copy); festoon catenary with gold bulbs |
| bow         | gold   | upright on x 262 (viewer's left), tip 112, frog 444; PARALLEL to the fiddle neck, never crossing it |
| fiddle      | gold   | upright on x 530 (viewer's right, the tall attribute), volute scroll ≈ 150, fist on the neck at 258, body 296–501, four Aquifer strings, jade fingerboard / tailpiece; four small gold T-pegs (Aquifer contour, two a side) inside the scroll's width |
| hands       | paper  | kit fists (§H.0 mitten, 3 finger lines, thumb over the top), h 34: bow (267, 424), wrist out along the hand axis (bend 50°) into a red cuff on a jade forearm from the band, the heel's pocket beside the frog paper; fiddle neck (530, 258), the heel against the neck, the wrist straight down into a red cuff (inner end under the neck) whose jade forearm rises hidden behind the body (art/_jh_hands.py) — the same red-cuff/jade-sleeve arm on both sides |
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from art import _jh_face as JF
from art import _jh_parts as JP
from art import _jh_head as JH_
from art import _jh_hands as JHH

P = K.P
HD = (-6.0, 2.0)                            # the head group's offset from its design position (392, 206)
HEAD = (392.0 + HD[0], 206.0 + HD[1])
FX = 530.0                                  # the fiddle's axis
BX = 262.0                                  # the bow stick's axis
SASH = ((268.0, 318.0), (375.0, 525.0))    # through the card centre: its 180° copy continues it
BAND_Y = 511.0                              # the court clip: beads and bulbs stay whole above it

# the fiddle hand (figure's left): the fist on the neck, the wrist straight into a red cuff that runs
# on behind the upper bout (the forearm rises behind the body)
FIST_R = (530.0, 258.0)
WR = (554.0, 286.5)                         # the hand's wrist point, on the cuff's top edge
CUFF_R = (552.5, 284.5)                     # the cuff's top-edge centre: its inner end runs in under the neck


TILT = -5.0                                 # the head bows toward the strings (screen degrees; − = counter-clockwise)
PIVOT = (392.0, 296.0)                      # ... about the throat, inside the collar


def tilt(part):
    """Rotate a head-group Part rigidly by TILT about PIVOT (no scale: strokes keep their widths)."""
    if not TILT:
        return part
    sh = shapely.affinity.rotate(part.shape, TILT, origin=PIVOT) if part.shape is not None else None
    return K.Part(sh, part.fills.rotate(TILT, *PIVOT), part.lines.rotate(TILT, *PIVOT), part.meta)


def H(*pts):
    """Head-group design points → card points."""
    out = [(x + HD[0], y + HD[1]) for x, y in pts]
    return out if len(out) > 1 else out[0]


BERET = H((350, 172), (338, 162), (342, 144), (388, 124), (446, 110), (492, 116), (508, 136), (502, 164), (486, 182),
          (464, 184), (440, 180), (400, 169), (364, 168))
BAND = H((358, 184), (442, 197))
PLUME = H((404, 160), (442, 126), (486, 100), (532, 86), (566, 90), (582, 112))
BOB = H((424, 196), (448, 194), (462, 214), (466, 246), (458, 272), (432, 281), (410, 272), (407, 254), (414, 238),
        (419.5, 222), (420, 208))
BOB_GUIDE = H((432, 188), (450, 212), (454, 244), (446, 274))


def figure(tunic_motif="rising"):
    sc = K.Scene(rank="J")
    fc = JF.minstrel_profile(HEAD, brow_dy=-16.0, brow_sag=3.0, nostril=(7.5, 0.6, -80.0, 3.4, 160.0))

    # ---- build every part first (the tunic's pattern is placed against what stays visible) ----
    tunic_d, tunic = JP.spline_region([(206, 360), (232, 342), (290, 326), (340, 310), (370, 300), (398, 305),
                                       (424, 299), (468, 310), (522, 324), (560, 338), (584, 362), (590, 545),
                                       (200, 545)])
    # the spline overshoots to x 612.6 at y 423–465, past the right sleeve's contour (a red chip against the
    # frame on both halves): the tunic stays under the sleeve
    tunic = tunic.intersection(K.box(0, 0, 598, 700))
    collar = JP.collar(H((371, 287)), H((425, 274)), H((361, 308)), H((431, 302)), bot_sag=5.0)
    clasp = K.lion_clasp((388.0, 333.5), 40.0)
    front_path = JP.open_spline([(404, 506), (402, 430), (398, 352)])[1]
    piping = JP.bead_chain(front_path, grow=(5.4, 8.4), gap=4.6,
                           keep=tunic.buffer(-3.5).intersection(K.box(0, 0, 750, BAND_Y - 4.2)))
    # the left puff's lower corner falls to the band well left of the forearm (at (182, 504) its outline met
    # the forearm's edge on the band rule: an ink wedge on the band, both halves)
    sleeveL = JP.puff_sleeve([(312, 318), (260, 310), (204, 321), (168, 350), (156, 402), (159, 460), (165, 500),
                              (205, 524), (270, 524), (286, 470), (296, 414), (304, 362)],
                             [((230.0, 296.0), (42.0, 53.0, 67.3), 38.0, 142.0),
                              ((224.0, 376.0), (38.0, 49.0, 63.3), 36.0, 144.0),
                              ((222.0, 448.0), (30.0, 41.0, 55.3), 34.0, 146.0)])
    sleeveR = JP.puff_sleeve([(446, 314), (502, 306), (556, 316), (592, 344), (605, 392), (606, 452), (606, 530),
                              (500, 530), (468, 470), (458, 404), (452, 356)],
                             [((528.0, 300.0), (40.0, 51.0, 65.3), 38.0, 142.0),
                              ((558.0, 378.0), (36.0, 47.0, 61.3), 36.0, 144.0),
                              ((562.0, 446.0), (30.0, 41.0, 55.3), 34.0, 146.0)])
    sash = JP.sash(SASH[0], SASH[1], 23.0, K.U(tunic, sleeveL.shape).buffer(-0.5), keep_above=BAND_Y - 4.2)
    # the bow hand's wrist out along its axis, the forearm from lower left (the back of the hand
    # angles away from the frog); the fiddle hand higher on the neck (the neck shows above the bout)
    hand_l = dict(shaft_w=20.0, back=-1, h=34.0)
    hand_r = dict(shaft_w=18.0, back=+1, h=34.0)
    FIST_L = (BX + 5.0, 424.0)
    WL = tuple(K.fist_wrist(FIST_L, -90.0, bend=50.0, **hand_l))
    forearm, cuff = K.sleeve(K.SleeveSpec(base=(196.0, 545.0), wrist=WL, sag=-4.0, width=46.0, wrist_w=32.0,
                                          cuff=12.0, folds=0, color=K.JADE, cuff_color=K.RED))
    bow = JP.bow(BX, 112.0, 444.0, 490.0, color=K.GOLD, stick_w=7.4, hair_dx=15.0, camber=3.5)
    handL = K.fist(FIST_L, -90.0, wrist=WL, wrist_w=26.0, **hand_l)
    fd = JP.Fiddle(x=FX, body_top=296.0, volute="spiral", scroll_r=21.5, pegbox_len=54.0, peg_t=(0.425, 0.60, 0.77, 0.94),
                   waist=(37.0, 100.0), fhole=(26.0, 92.0, 29.0, 140.0, 3.8), bridge_ext=5.0,
                   pegs="T", tpeg=(3.0, 6.0, 6.5, 12.0))
    neck_, body_ = fd.neck_part(), fd.body_part()
    # the left forearm rises behind the body: only its red cuff shows, under the fist
    armR, cuffR = JHH.fiddle_arm(CUFF_R, (552.0, 420.0), 36.0, 34.0,
                                 K.U(fd.body_region().buffer(-3.0), K.box(0, 0, 750, 330)))
    # the wrist drops straight into the cuff (a short wrist: the cuff is right under the back of the
    # hand, its forearm hidden) — hidden_wrist: the kit's bend check is for a visible forearm
    handR = K.fist(FIST_R, -90.0, wrist=WR, wrist_w=26.0, hidden_wrist=True, **hand_r)

    # the tunic: Gill Red, rising bubbles knocked out to paper where it stays uncovered
    front = K.U(collar.shape, clasp.shape.buffer(6.0), sleeveL.shape, sleeveR.shape, sash.shape, forearm.shape,
                cuff.shape, bow.shape.buffer(K.HALO + 2), handL.hand.shape, body_.shape, neck_.shape,
                handR.hand.shape, armR.shape, cuffR.shape, K.box(0, 505, 750, 600),
                LineString(front_path).buffer(9.0))
    visible = tunic.difference(front)
    motif = {"rising": JP.rising, "triad": JP.triad}.get(tunic_motif)
    tfill = K.fill(tunic, K.RED)
    if motif is not None:
        pw = JP.powder(tunic, motif, pitch=(30.0, 34.0), origin=(400.0, 330.0), visible=visible,
                       clear=K.CONTOUR / 2 + 3.0)
        tfill = C.fill(C.knockout(K.D(tunic), pw), color=K.RED, role="fill")

    # ---- the stack, back to front ------------------------------------------------
    face_ = tilt(K.Part(fc.skin, C.Frag(), fc.lines + K.outline(fc.head), {}))
    sc.part("head", face_)                                             # the neck runs down under the collar
    sc.part("tunic", K.Part(tunic, tfill, K.outline(tunic), {}))
    sc.add("piping-front", piping, None, sil=False)
    sc.part("collar", collar)
    sc.part("clasp", clasp)

    # hair, beret, plume, brooch: the bob covers the skull under the beret and the back of the head
    # behind its front edge (no paper pocket between the nape and the hair)
    _, edge = JP.open_spline(H((412, 190), (419, 204), (419.5, 222), (414, 238), (407, 254), (407, 272)))
    behind = Polygon(np.vstack([np.asarray(edge), [H((412, 285)), H((480, 285)), H((480, 150)), H((412, 150))]]))
    collar_up = shapely.affinity.rotate(collar.shape, -TILT, origin=PIVOT)      # the collar in the head's frame
    sc.part("hair", tilt(JH_.bob(BOB, BOB_GUIDE, filler=behind.intersection(K.U(fc.skin, K.box(395, 200, 440, 275))),
                                 around=(fc.skin, collar_up))))
    sc.part("beret", tilt(JH_.soft_beret(BERET, BAND, 18.0, fc.skin, ripple=(14.0, 1.6), under_hatch=14.0,
                                         under_x1=482.0)))
    sc.part("plume", tilt(JP.plume_locks(PLUME, n=4, ends=(1.0, 0.92, 0.84, 0.76), tip_curl=(12.0, 200.0),
                                         curl_deg=110.0, smooth=10.0)))
    # the heart in a paper channel knocked out of the gold bezel, the bezel's contour MEDIUM (the old
    # 3.4 px bezel with two contours was cut by heal to a contourless ring with bites out of the heart)
    # (2.5 px up the quill: its tip clears the band's ripple by 3 px)
    brooch_c = (PLUME[0][0] + 1.0, PLUME[0][1] - 2.5)
    sc.part("brooch", tilt(JP.fluke_heart(brooch_c, u=17.5, bezel=6.2, ring=3.0)))

    # the puffed sleeves, the sash over the left one
    sc.part("sleeveL", sleeveL)
    sc.part("sleeveR", sleeveR)
    sc.part("sash", sash)

    # the left forearm and the bow
    sc.part("forearmL", forearm)
    sc.part("bow", bow, halo=K.HALO, halo_only=("sash", "sleeveL", "tunic"), sil=False)
    sc.part("cuffL", cuff)
    # the heel's pocket beside the frog: paper, like the frog's own channel (not a 3 px jade sliver)
    JHH.heel_paper(sc, "handL~pocket", handL.tucked(sc).shape, bow.shape, halo=K.HALO, only=("sleeveL",),
                   arms=(forearm.shape, cuff.shape), box=(232.0, 440.0, 258.0, 480.0))
    handL.add_to(sc, "handL", halo=0.0)

    # the left arm and the fiddle: the T-pegs behind the pegbox (their shafts run in under its cheeks);
    # the cuff behind the neck (its inner end runs in under it), the fist in front, the body over the forearm
    sc.part("fiddle-pegs", fd.tpegs_part(), sil=False)
    sc.part("forearmR", armR)
    sc.part("cuffR", cuffR)
    sc.part("fiddle-neck", neck_)
    JHH.seat_on_neck(sc, "handR", handR, neck_.shape, cuffR.shape, shaft_x=FX,
                     y_fingers=FIST_R[1] + K.fist_geom(FIST_R, -90.0, **hand_r)["y1"], y_cuff=CUFF_R[1],
                     back_x0=FX + 14.0)
    sc.part("fiddle-body", body_)
    return sc


def build():
    return figure().layers()
