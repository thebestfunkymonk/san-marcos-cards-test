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
| brooch      | red    | fluke heart u 17 (a pip) in a 3 px paper channel knocked out of a 7.4 px gold bezel (2.85 px of gold shows) with a MEDIUM contour (the pin of the plume) |
| collar      | jade   | standing collar, top 289 at the throat rising to 276 under the bob, foot ≈ 304–312; gold beads |
| tunic       | red    | shoulders ≈ 300–330 to the band; gold bubble-chain piping down the front; paper bubbles knocked out |
| clasp       | gold   | Lion Mark 40 px at (388, 333.5), clear of the collar's foot |
| sleeves     | jade   | puffed upper sleeves, slashed with ripple arcs (paper); the right puff's inner edge ≥ 9 px off the fiddle's lower bout |
| sash        | paper  | 46 wide, (268, 318) → the card centre (continues across the band in the 180° copy); festoon catenary with gold bulbs |
| bow         | gold   | upright on x 261 (viewer's left), tip 112, frog 454–476 (6 px of stick shows under the fist), button to 490; PARALLEL to the fiddle neck, never crossing it; in front of the left shoulder's CONTOUR too (``compose``: the silhouette line stops at its paper channel) |
| fiddle      | gold   | upright on x 530 (viewer's right, the tall attribute), volute scroll ≈ 150, fist on the neck at 254, body 296–501, four Aquifer strings, jade fingerboard (lying ON the body: the bout line ends at its edges) / tailpiece; four small gold T-pegs (Aquifer contour, two a side) inside the scroll's width |
| hands       | paper  | kit fists (§H.0 mitten, 3 finger lines, thumb over the top), h 34: bow (268, 424: the stick's edge lands on the thumb's top, clear of its tip), wrist out along the hand axis (bend 50°) into a red cuff on a jade forearm from the band, the heel's pocket beside the frog and button paper down to the button channel's floor, ending level; the underside level; fiddle neck (530, 254), the heel against the neck, the wrist (bend 63°) into a red cuff leaning 20° whose inner end runs under the neck and whose lower edge lies behind the upper bout (its outer side crosses the bout at ≈ 50°; the jade forearm is hidden) (art/_jh_hands.py) — the same red-cuff/jade-sleeve arm on both sides; the backs of both hands smoothed where the knuckle round meets the wrist; the fiddle fist's index and little-finger bands kept level where the neck's far edge meets them |
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
BX = 261.0                                  # the bow stick's axis
SASH = ((268.0, 318.0), (375.0, 525.0))    # through the card centre: its 180° copy continues it
BAND_Y = 511.0                              # the court clip: beads and bulbs stay whole above it

# the fiddle hand (figure's left): the fist on the neck, the wrist into a red cuff that runs in under
# the neck and on behind the upper bout (the forearm rises behind the body)
FIST_R = (530.0, 254.0)
WR = (562.0, 289.0)                         # the hand's wrist point, on the cuff's top edge (bend 63° ≤ 65°)
LEAN_R = 20.0                               # the forearm leans 20° (elbow down-left, behind the body)
CUFF_LR = (28.0, 20.0)                      # the cuff's top edge: 28 px left of the wrist (under the neck), 20 right


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
                              (205, 524), (276, 524), (296, 470), (304, 414), (306, 362)],
                             [((230.0, 296.0), (42.0, 53.0, 67.3), 38.0, 142.0),
                              ((224.0, 376.0), (38.0, 49.0, 63.3), 36.0, 144.0),
                              ((222.0, 448.0), (30.0, 41.0, 55.3), 78.0, 146.0)])
    # the right puff's inner edge keeps ≥ 6 px of paper off the fiddle's lower bout and meets the band left
    # of the body (at (500, 530) / (468, 470) it ran 1.1 px from the bout's outline for ≈ 25 px: a
    # near-miss heal answered by cutting 27 px out of the body's outline — gold straight onto jade)
    sleeveR = JP.puff_sleeve([(446, 314), (502, 306), (556, 316), (592, 344), (605, 392), (606, 452), (606, 530),
                              (482, 530), (459, 468), (455, 404), (452, 356)],
                             [((528.0, 300.0), (40.0, 51.0, 65.3), 38.0, 134.0),
                              ((558.0, 378.0), (36.0, 47.0, 61.3), 36.0, 144.0),
                              ((562.0, 446.0), (30.0, 41.0, 55.3), 34.0, 146.0)])
    sash = JP.sash(SASH[0], SASH[1], 23.0, K.U(tunic, sleeveL.shape).buffer(-0.5), keep_above=BAND_Y - 4.2)
    # the bow hand's wrist out along its axis, the forearm from lower left (the back of the hand
    # angles away from the frog); the fiddle hand higher on the neck (the neck shows above the bout)
    hand_l = dict(shaft_w=20.0, back=-1, h=34.0)
    hand_r = dict(shaft_w=18.0, back=+1, h=34.0)
    FIST_L = (268.0, 424.0)
    WL = tuple(K.fist_wrist(FIST_L, -90.0, bend=50.0, **hand_l))
    forearm, cuff = K.sleeve(K.SleeveSpec(base=(196.0, 545.0), wrist=WL, sag=-4.0, width=46.0, wrist_w=32.0,
                                          cuff=12.0, folds=0, color=K.JADE, cuff_color=K.RED))
    bow = JP.bow(BX, 112.0, 454.0, 490.0, color=K.GOLD, stick_w=7.4, hair_dx=15.0, camber=3.5, frog_h=22.0)
    handL = K.fist(FIST_L, -90.0, wrist=WL, wrist_w=26.0, **hand_l)
    fd = JP.Fiddle(x=FX, body_top=296.0, volute="spiral", scroll_r=21.5, pegbox_len=54.0, peg_t=(0.425, 0.60, 0.77, 0.94),
                   waist=(37.0, 100.0), fhole=(26.0, 92.0, 29.0, 140.0, 3.8), bridge_ext=5.0,
                   pegs="T", tpeg=(3.0, 6.0, 6.5, 12.0))
    neck_, body_ = fd.neck_part(), fd.body_part(fb_over=True)    # the fingerboard lies on the body
    # the left forearm rises behind the body: only its red cuff shows, under the fist, its lower edge
    # well behind the upper bout (its outer side runs in behind the bout at a clear angle)
    armR, cuffR, _ = JHH.fiddle_arm(WR, LEAN_R, CUFF_LR[0], CUFF_LR[1], fd.body_region().buffer(-3.0))
    # the wrist arrives upright (the forearm turns away behind the body under the cuff)
    handR = K.fist(FIST_R, -90.0, wrist=WR, wrist_w=26.0, arm=(0.0, 1.0), **hand_r)

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
    brooch_c = (PLUME[0][0] + 1.0, PLUME[0][1] - 3.7)
    sc.part("brooch", tilt(JP.fluke_heart(brooch_c, u=17.0, bezel=7.4, ring=3.0)))

    # the puffed sleeves, the sash over the left one
    sc.part("sleeveL", sleeveL)
    sc.part("sleeveR", sleeveR)
    sc.part("sash", sash)

    # the left forearm and the bow
    sc.part("forearmL", forearm)
    sc.part("bow", bow, halo=K.HALO, halo_only=("sash", "sleeveL", "tunic"), sil=False)
    sc.part("cuffL", cuff)
    # the heel's pocket beside the frog: paper, like the frog's own channel (not a 3 px jade sliver),
    # down to the floor of the button's channel and level there (no hump of jade between two hollows)
    JHH.heel_paper(sc, "handL~pocket", handL.tucked(sc).shape, bow.shape, halo=K.HALO, only=("sleeveL",),
                   arms=(forearm.shape, cuff.shape), box=(232.0, 440.0, 262.0, 505.0),
                   floor=490.0 + K.HALO + K.MEDIUM / 2)
    # ... and the corner between the stick's channel and the top of the fist (a 3 px jade dot)
    JHH.heel_paper(sc, "handL~top", handL.tucked(sc).shape, bow.shape, halo=K.HALO, only=("sleeveL",),
                   arms=(forearm.shape, cuff.shape), box=(240.0, 394.0, 259.0, 410.0), close=4.0)
    # the stick's and the hair's lines end a little inside the fist's outline (clipped at its edge
    # they end in round caps that bump its line where they meet it, above and below the fist)
    hl_shape = handL.tucked(sc).shape
    sc.add("handL~caps", C.Frag(), hl_shape.buffer(1.2).intersection(K.box(BX - 8.0, 380.0, BX + 22.0, 460.0))
           .intersection(bow.shape.buffer(K.MEDIUM)), sil=False)
    gL = K.fist_geom(FIST_L, -90.0, **hand_l)
    handL = JHH.smooth_back(handL, sc, K.box(216.0, 398.0, 247.0, 438.0), 25.0, cuff=cuff.shape,
                            flat=(FIST_L[0] - gL["a"] - K.PARALLEL_MIN - 0.6, FIST_L[0] - gL["a"] + 0.4,
                                  FIST_L[1] + gL["y1"]))
    handL.add_to(sc, "handL", halo=0.0)

    # the left arm and the fiddle: the T-pegs behind the pegbox (their shafts run in under its cheeks);
    # the cuff behind the neck (its inner end runs in under it), the fist in front, the body over the forearm
    sc.part("fiddle-pegs", fd.tpegs_part(), sil=False)
    sc.part("forearmR", armR)
    sc.part("cuffR", cuffR)
    sc.part("fiddle-neck", neck_)
    gR = K.fist_geom(FIST_R, -90.0, **hand_r)
    JHH.seat_on_neck(sc, "handR", handR, neck_.shape, cuffR.shape, shaft_x=FX,
                     y_fingers=FIST_R[1] + gR["y1"], own_cut=True, back_x0=FX + 14.0, back_close=25.0,
                     level=(FIST_R[1] + gR["y1"] - gR["hb"], FIST_R[1] + gR["y1"]))
    sc.part("fiddle-body", body_)
    return sc


def compose(sc, cut_y=BAND_Y):
    """``Scene.compose`` with the bow IN FRONT of the silhouette line too.

    The bow is drawn with ``sil=False`` (a MEDIUM outline, not the figure's
    CONTOUR) and a paper channel over the sleeve, sash and tunic; but the
    kit adds the silhouette line after the painter's clip, so the left
    shoulder's CONTOUR would run straight across the stick and the hair (a
    plain crossing, §I.13, as if the bow were behind the shoulder). Here the
    CONTOUR stops at the bow's channel where the stick crosses the shoulder,
    as every line behind the bow already does (the Q♦ paintbrush, the Q♥ /
    K♦ / Q♣ staffs); then the kit's heal, against the band rule as in
    ``Scene.compose``."""
    res = sc.compose(heal_gaps=False)
    bow_it = next(it for it in sc.items if it.name == "bow")
    ch = bow_it.occ.buffer(bow_it.halo + K.MEDIUM / 2, quad_segs=12).intersection(K.box(BX - 30.0, 250.0, BX + 40.0, 370.0))
    con = res.select(lambda m: m.role == "contour")
    rest = res.select(lambda m: m.role != "contour")
    res = rest + K.clip_out(con, Polygon(), halo=ch)
    band = C.stroke(f"M100 {K._f(cut_y)}L650 {K._f(cut_y)}", K.FINE, style="rule", role="_band")
    log = []
    res = K.heal(res + band, log=log, keep_roles=("contour", "_band"))
    sc.heal_log = log
    return res.select(lambda m: m.role != "_band")


def build():
    return K.layers(compose(figure()))
