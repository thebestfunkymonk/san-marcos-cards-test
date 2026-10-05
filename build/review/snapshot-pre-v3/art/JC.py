"""art/JC.py — J♣ · The River Squire (House of the Reed), creative brief §H.9.

Built with deck.courtkit (the K♠'s hand) plus art/_jc_head.py (hair, heron
plume), art/_jc_body.py (doublet, jerkin, sleeves, belt), art/_jc_hands.py
(the hand on the belt), art/_jc_paddle.py (the paddle) and art/_jc_parts.py
(flat cap, collar, club brooch, husk buckle).

Composition (follow-up pass: a river squire, not Robin Hood)

| part      | colour | geometry |
|-----------|--------|----------|
| head      | paper  | kit 3/4-left face at (385, 207), young, raised lids, pupils 3 px downstream hanging from the lids (tuck −0.4) |
| cap       | jade   | Tudor flat cap: soft flat crown (ellipse 68 × 19 about (398, 147)), its gathered underside half-hatched; a rolled brim round the brow (band 14 deep on the front arc r 50 × 7 about (388, 174)) — no peak |
| brooch    | gold   | round boss r 12.5 at (448, 164) with the ♣ pip set in Aquifer; pins the plume |
| plume     | paper  | great-blue-heron plume: S from the brooch up and back, round terminal at (522, 78) — ≥ 12 px inside the gold rule, clear of the paddle; 2 current lines 7.6 apart, staggered 16 px, rolling the same way (50°) into terminals, gold quill |
| hair      | gold   | page-boy bob, 4 current lines (ends staggered 168/152/118/98); far lock under the brim |
| collar    | jade   | short standing collar round the neck (top 286–296, foot 310–321) |
| clasp     | gold   | Lion Mark 40 px at (370, 340), on the doublet front |
| doublet   | jade   | the bust, showing at the sides and the front opening; its puffed sleeves carry §G.18 comb sprays in Aquifer |
| jerkin    | red    | sleeveless and waisted (armholes in to x 278 / 472 at the waist, the doublet's side showing under both arms); the far edge runs on under the resting hand and leaves the little finger's side at ~62° as the skirt's flare; the near edge passes ≥ 13 px left of the loom hand, cuff and forearm to meet the belt's top edge square, then hides under the belt and forearm: plain Gill Red — no motif on the red (§C.4) |
| guards    | gold   | §G.19 reed-ladder braid down the front opening to the buckle |
| belt      | jade   | reed stalk knocked out, nodes every 47 px from 4 px past the buckle (whole or hidden; ≈ 409 / 456, clear of the near jerkin edge's foot), the stalk running on under the buckle, the hands and the loom forearm; pecan-husk buckle (gold) at (358, 444); comes out from under the resting hand (the pockets the left arm cuts off are left out) and runs on behind the loom forearm and ends there |
| paddle    | jade/gold | upright like a halberd at x 548, blade tip y 100, half-hatched, gold band |
| forearms  | jade   | one comb spray each, elbow → wrist; red cuffs. Viewer's left: elbow just under the puffed sleeve, cuff 251–264 × 409–442 (above the belt's top edge) flush with the forearm; viewer's right: from below the band to the wrist at bend 40° / 0.9 (courtkit.fist_wrist), the belt's edges meeting its straight contour ≥ 10 px under the cuff |
| hands     | paper  | the squire's right hand draped over the belt, back to us (courtkit.flat via _jc_hands.rest_hand: 72 × 32 pointing 55°, the wrist leaving the cuff along the forearm ~5 px inside both its corners and turning down; thumb 26° off the index with a web crease, crossing the belt's top edge at ~31°, its tip 12.6 px off the husk, its tip and web ≥ 10 px above the bottom edge; fingers softly curled, the index crossing the bottom edge at ~53°); his left fist on the loom at (548, 388), from the body side (palm view) |
"""
from __future__ import annotations

import os
import sys

import numpy as np
from shapely.geometry import Point, Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K  # noqa: E402
import _jc_body as B  # noqa: E402
import _jc_hands as JH  # noqa: E402
import _jc_head as H  # noqa: E402
import _jc_paddle as PD  # noqa: E402
import _jc_parts as J  # noqa: E402

HEAD = (385.0, 207.0)
PADDLE_X = 548.0
FIST = (548.0, 388.0)
FIST_KW = dict(shaft_w=22.0, back=-1, h=36.0)
WL = (263.0, 440.0)
# round-1 belt hand (courtkit.flat via _jc_hands.belt_hand) — used only when
# HAND_L2 is None; round 2 draws the hand with HAND_L2 (see below)
HAND_L = dict(side=-1, length=58.0, width=33.0, wrist_w=24.0, tips=(5.0, 0.0, 3.0, 9.0), knuckle=0.48, curl=8.0,
              thumb_deg=46.0, thumb_len=0.42, stub=K.HAND_STUB)
HAND_L_ANGLE = 38.0
HAND_L_KW = dict(crease="web", ulnar_r=5.0, radial_r=8.0, crease_len=0.24, crease_sag=1.0)
WR_BEND, WR_DIST = 40.0, 0.9
WR = tuple(K.fist_wrist(FIST, -90.0, bend=WR_BEND, dist=WR_DIST, **FIST_KW))    # out along the hand's axis
BELT_Y = 440.0
# raised (alert) lids, pupils thrown 3 px downstream and hanging from the lids
# (pupil_tuck −0.4): the raised preset's −1.8 lifted the 70 % far pupil ABOVE
# its RULE lid (a bump on the lid, the far eye empty at card size) and hid
# half the near one — the gaze read rolled-up and vacant
FACE_KW = dict(lids="raised", pupil_dx=-3.0, pupil_tuck=-0.4)
# the near fall's current-line ends (px along its outer edge)
HAIR_ENDS = [168.0, 152.0, 118.0, 98.0]      # staggered so no two terminals crowd (was 168/148/128/108)
# the kit's heel pocket (the ground between the loom fist's heel, its cuff and
# the loom's channel turned to paper) is dropped here: with the forearm rising
# from the body side it lands BELOW the heel as a detached white tab between
# the forearm and the channel; the doublet reads on in plain jade instead
DROP_HEEL_POCKET = True
BELT_RISE = (2.0, 4.0)
# the belt runs on behind the loom forearm and stops there (see figure())
BELT_END_UNDER_FOREARM = True
# reed nodes every 47 px from 4 px past the buckle (x ≈ 409, 456): both stay
# whole between the buckle and the loom forearm (58 put the second one half
# under the forearm; 48/2 and 50/0 cut the first against the husk). (round 3)
# r2's 54 set the second ring's right side exactly under the near jerkin
# edge's foot on the belt (x 472.5): the edge read as running on through the
# belt into the ring; the ring now ends ~10 px short of it
BELT_NODES = (47.0, 4.0)

# the flat cap and its plume. The plume is pinned by the club brooch on the
# cap's side and streams back in an S; its round tip stays ≥ 12 px inside the
# gold rule (and far from the top-right chamfer) and clear of the paddle blade
CAP = dict(roll_c=(388.0, 174.0), roll_r=(50.0, 7.0), roll_h=14.0, crown_c=(398.0, 147.0), crown_r=(68.0, 19.0),
           crown_rot=-2.0)
BROOCH = (448.0, 164.0)
BROOCH_KW = dict(r=12.5, u=12.0, dy=0.0)
PLUME = [(448, 164), (457, 140), (462, 116), (476, 97), (497, 86), (522, 78)]
# (round 2) two current lines of like length 7.6 apart, the inner one ending
# 16 px before the outer, both rolling the same way through a gentle 50° into
# their terminals — in a vane 2 px fuller (w_max 30) so each terminal keeps
# ≥ 3 px of paper from the contour and the other line (the r1 inner line was
# clipped to a 13 px 'tadpole'; 90° curls hit the contour and heal cut them)
PLUME_KW = dict(w_max=30.0, w_root=11.0, quill=34.0, quill_w=11.0, quill_back=4.0, swell=0.42, tip_pow=0.8,
                vane_from=24.0, tip_r=4.5, bulb=1.8,
                lines=((-3.8, 42.0, -52.0, -1), (3.8, 40.0, -36.0, -1)), curl_deg=50.0)
COLLAR = dict(top=((344.0, 289.0), (414.0, 286.0)), top_sag=-7.0, foot=((338.0, 314.0), (420.0, 310.0)),
              foot_sag=-7.0)
CLASP = (370.0, 340.0)
BUTTONS = ((363.5, 372.0), (361.2, 396.0))

# the body: the jade doublet (the whole bust) under a sleeveless, waisted red
# jerkin whose front opening is edged with gold reed-ladder braid
TORSO = ([(342, 301), (300, 310), (266, 322), (244, 340)], [(244, 340), (246, 420), (244, 530)],
         ("L", [(244, 530), (536, 530)]), [(536, 530), (538, 420), (536, 340)],
         [(536, 340), (512, 322), (466, 308), (418, 300)], ("L", [(418, 300), (342, 301)]))
# the jerkin's near (viewer's-right) armhole edge. (round 3) It curves in to the
# waist (x 472 at the belt's top edge, which it meets square) passing LEFT of
# the loom hand, its cuff and forearm (≥ 13 px clear), so the doublet's side
# shows under the arm as it does on the far side, and the red cuff sits on
# jade; below the belt it runs hidden under the belt and the forearm (≥ 7 px
# inside its contours). The r2 edge (hidden under the wrist, cuff and forearm
# below y 392) left the red cuff's end butting on the red jerkin (same colour
# touching, COURT_GUIDE §9) and ran along the forearm's contour near the band.
JERK_R_LOW = [(502, 540), (502, 482), (490, 452), (473, 434)]
JERK_R_HIGH = [(474, 420), (480, 404), (489, 385), (498, 362), (504, 340), (500, 314)]


# the jerkin's far (viewer's-left) armhole edge. (round 3) It runs on hidden
# under the resting hand to a corner under the little finger and comes out
# from under that finger's side as the skirt's flare (a gentle arc 125° → 106°
# to the band): it meets the finger at ~62°, 32 px from the cuff's corner. The
# r2 edge (… (278, 428), (272, 470), (260, 540)) came out of the back of the
# hand 26° off its ulnar edge, 19 px under the cuff — the two read as one
# kinked line from the cuff to the band, with a thin red wedge between them
JERK_L = [(276, 316), (268, 346), (272, 390), (278, 428), (284, 463)]
JERK_L_LOW = [("S", [(284, 463), (262, 512)], 125.0, 106.0), ("L", [(262, 512), (259, 540)])]


def jerk():
    low = [] if JERK_L_LOW is None else (list(JERK_L_LOW) if isinstance(JERK_L_LOW, list) else [JERK_L_LOW])
    left = [JERK_L] + low
    return ([(342, 301), (304, 306), (276, 316)], *left,
            ("L", [(260, 540), JERK_R_LOW[0]]), JERK_R_LOW + JERK_R_HIGH,
            [(500, 314), (464, 305), (418, 300)], ("L", [(418, 300), (342, 301)]))


JERK = jerk()
E_L = [(334, 302), (338, 350)]
E_R = [(410, 300), (390, 360)]
# §G.18 comb sprays in Aquifer on the jade, along the puffed sleeves
# (following the puff); the doublet's narrow side strips stay plain (a spray
# there loses its ticks to the seams)
DOUBLET_SPRAYS = []
SLEEVE_L = [K.arc_sag((238.0, 334.0), (214.0, 442.0), -7.0), K.arc_sag((208.0, 344.0), (184.0, 436.0), -9.0)]
SLEEVE_R = [K.arc_sag((550.0, 334.0), (564.0, 522.0), 6.0), K.arc_sag((578.0, 350.0), (586.0, 522.0), 8.0)]
# the forearms: the viewer's-left one from the elbow at the belt to its red
# cuff; the viewer's-right one rises from below the band to the loom. Each
# carries one comb spray from the elbow toward the wrist (so the jade
# forearm reads against the jade doublet and puff behind it)
# (round 2: the whole viewer's-left forearm and cuff sit 15 px higher, so the
# hand's wrist and thumb root ride above the belt and the hand drapes DOWN
# across it — every belt edge meets the hand at 35°+, none runs along it)
FOREARM_L = ([(204, 419), (258, 409)], ("L", [(258, 409), (258, 441)]),
             [(258, 441), (220, 465), (196, 467), (180, 451), (182, 431), (204, 419)])
FOREARM_L_SPRAY = "M198 443L244 428"
CUFF_L = ((251.5, 409.5), (252.5, 442.5), 12.0)
ARM_R_INNER = [(530, 530), (535, 440), (530, 370), (508, 316)]
SLEEVE_R_SPEC = dict(base=(476.0, 552.0), sag=-3.0, width=50.0, wrist_w=32.0, cuff=12.0)
FOREARM_R_SPRAY = "M490 498L506 440"      # (round 2) up the longer forearm (fist at 388), its foot clear of the band


def guard_stop(edge, side, width, extend, obstacle, clip):
    """The clip for a guard that runs INTO ``obstacle`` (the buckle): the
    guard stops square across its width where its first rail passes under
    the obstacle, so no tapering sliver of braid is left beside it
    (QA 5r, thin gold on red)."""
    ep = B.pts_of(B.spl(edge), 0.3)
    t0 = K.G.Curve(ep).tangent_s(0.0)
    ep = np.vstack([[ep[0] - t0 * extend[0]], ep])
    cv = K.G.Curve(ep)
    inner = obstacle.buffer(-2.0)
    s_cut = cv.length
    for rail in (ep, cv.offset(side * width, spacing=0.3)):
        rc = K.G.Curve(rail)
        hit = next((sv for sv in np.arange(0.0, rc.length, 0.5) if inner.contains(Point(*rc.at_s(sv)))), None)
        if hit is not None:
            s_cut = min(s_cut, hit * cv.length / rc.length)
    p, t = cv.at_s(s_cut), cv.tangent_s(s_cut)
    n = np.array([t[1], -t[0]])
    beyond = K.halfplane(p - n * 100.0, p + n * 100.0, side=+1)
    if not beyond.contains(Point(*(p + t * 5.0))):
        beyond = K.halfplane(p - n * 100.0, p + n * 100.0, side=-1)
    return K.R(clip).difference(beyond)


# round 2: the viewer's-left arm as one piece — forearm capsule, cuff square to
# it, the hand's wrist coming out of the cuff along the forearm and turning
ARM_L = None            # dict(elbow=, wrist=, r_elbow=, w_wrist=) or None (the hand-drawn FOREARM_L / CUFF_L)
# the squire's right hand resting on the belt, draped down across it (round 2):
# the wrist leaves the cuff along the forearm and turns down (_jc_hands.rest_hand),
# the thumb lies along the index 26° off it (12 px free past the web) and
# crosses the belt's top edge at ~33°, its web and tip ≥ 10 px above the bottom
# edge (the r1 thumb, opened 46°, ran 2 px under the top edge and parallel to it)
# (round 3) 72 × 32 (was 65 × 31): the squire's hand was a tenth shorter than
# the Q♥'s (72 × 31) and ~0.68 of his face; the thumb ratio .46 → .44 keeps its
# tip 12.6 px off the husk and its crossing of the belt's top edge at ~31°
HAND_L2 = dict(angle=55.0, lead=5.0, sweep_r=6.0, side=-1, length=72.0, width=32.0, wrist_w=24.0,
               tips=(5.0, 0.0, 3.0, 9.0), knuckle=0.46, curl=10.0, thumb_deg=26.0, thumb_len=0.44,
               crease="web", ulnar_r=5.0, radial_r=8.0, crease_len=0.24, crease_sag=1.0,
               ulnar_round=8.0, ulnar_lead=4.0, radial_round=8.0)


CUFF_L_FLARE = (0.0, 0.0)     # the hand-side edge runs this much past the top chord's ends (top, bottom)


def _arm_l():
    """(forearm region, cuff Part) of the viewer's-left arm."""
    if ARM_L is None:
        return B.region(*FOREARM_L), B.cuff(*CUFF_L, flare=CUFF_L_FLARE)
    a = dict(ARM_L)
    sag = a.pop("sag", 2.5)
    a.pop("spray", None)
    reg, (p0, p1) = JH.forearm(a.pop("elbow"), a.pop("wrist"), **a)
    return reg, B.cuff(p0, p1, 12.0, sag=sag)


def belt_band():
    """the belt's band region (no pattern) — what the hooked thumb goes behind"""
    return B.reed_belt(K.box(0, 0, 750, 1050), y=BELT_Y, h=24.0, sag=4.0, x0=220.0, x1=560.0, front=358.0,
                       rise=BELT_RISE, node_every=1000.0).shape


BELT_FROM_HAND = True        # the belt starts under the resting hand (see figure())


def belt_pockets(front, clip):
    """The pieces of the belt's band (inside ``clip``) that ``front`` (the
    viewer's-left forearm, cuff and hand) cuts off from the main run of the
    belt, each grown 1 px (under the covering contours) — the region to leave
    out of the belt."""
    band = K.R(belt_band()).intersection(K.R(clip))
    vis = band.difference(K.R(front))
    pieces = K._polys_of(vis)
    main = max(pieces, key=lambda g: g.area) if pieces else None
    out = [g for g in pieces if g is not main and g.centroid.x < main.centroid.x]
    if not out:
        return Polygon()
    return K.U(*out).buffer(1.0)


def _hands():
    """the right hand rests on the belt, back to us, thumb opened off the index
    (courtkit.flat via _jc_hands.belt_hand, cut on the cuff's edge); the left
    grips the loom from the body side, seen from the palm (hand='L')"""
    fl, cuffL = _arm_l()
    if HAND_L2 is None:
        handL = JH.belt_hand(WL, HAND_L_ANGLE, cuff=(cuffL.shape, cuffL.meta["inner_edge"]), **HAND_L_KW, **HAND_L)
    else:
        hk = dict(HAND_L2)
        ang = hk.pop("angle")
        hide = belt_band() if hk.pop("hide", False) else None
        e0, e1 = cuffL.meta["inner_edge"]
        w = (K.P(e0) + K.P(e1)) / 2 + K.P(hk.pop("shift", (0.0, 0.0)))
        if ARM_L is not None:
            fore = w - K.P(ARM_L["elbow"])
        else:
            c0, c1 = K.P(CUFF_L[0]), K.P(CUFF_L[1])
            fore = K.P((c1 - c0)[1], -(c1 - c0)[0])
        handL = JH.rest_hand(w, ang, fore=fore, cuff=(cuffL.shape, cuffL.meta["inner_edge"]), hide=hide, **hk)
    handR = K.fist(FIST, -90.0, wrist=WR, wrist_w=26.0, hand="L", **FIST_KW)
    return handL, handR


def figure():
    sc = K.Scene(rank="J")
    # the kit's 3/4-left face (the J♦'s hand, mirrored): young, raised lids,
    # the pupils thrown 3 px downstream (left), hanging from the lids (FACE_KW)
    fc = K.face(HEAD, "3/4-left", age="young", **FACE_KW)

    # ---- the front objects first (their shapes keep the comb sprays clear) ----------
    torso = B.region(*TORSO)
    e_l = [tuple(p) for p in E_L] + [(358, BELT_Y - 4.0)]
    e_r = [tuple(p) for p in E_R] + [(358, BELT_Y - 4.0)]
    s_l = [(358, BELT_Y + 8.0), (345, 490), (330, 530)]
    s_r = [(358, BELT_Y + 8.0), (372, 490), (388, 530)]
    v_top = B.region(e_l, e_r[::-1], ("L", [(410, 300), (334, 302)]))
    v_bot = B.region(s_l, ("L", [(330, 530), (388, 530)]), s_r[::-1])
    vee = K.U(v_top, v_bot)
    jer = B.region(*jerk()).intersection(torso).difference(vee)
    BUCKLE = (358.0, BELT_Y + 4.0)
    husk = J.pecan_husk(BUCKLE, style="D", s=1.25)
    fl, cuffL = _arm_l()
    slR, cfR = K.sleeve(K.SleeveSpec(wrist=WR, folds=0 if FOREARM_R_SPRAY else 1, color=K.JADE, cuff_color=K.RED,
                                     **SLEEVE_R_SPEC))
    paddle = PD.paddle3(PADDLE_X, tip=100.0, square=24.0, hw=29.0, widest=210.0, shoulder=266.0,
                        band=(240.0, 256.0), taper=0.70, throat=288.0, grip_rings=((318.0, 3),), blade_color=K.JADE)
    handL, handR = _hands()
    hands = K.U(handL.hand.shape, handL.thumb.shape, handR.hand.shape, handR.thumb.shape)
    arm_front = K.U(fl, cuffL.shape, slR.shape, cfR.shape, paddle.shape.buffer(K.HALO), hands)
    belt_clip = torso
    if BELT_FROM_HAND:
        # the belt comes out from under the resting hand: any piece of the band
        # the forearm, cuff and hand cut off from the rest (the notches between
        # the cuff and the tapering wrist) is left out, so the doublet shows
        # there and no belt edge runs out of the cuff alongside the wrist
        belt_clip = belt_clip.difference(belt_pockets(K.U(fl, cuffL.shape, handL.hand.shape), belt_clip))
    if BELT_END_UNDER_FOREARM:
        # the belt runs on behind the loom forearm and stops there: the ~10 px of
        # it that would show between the forearm and the loom's channel is a
        # knot of short edges round the heel and the cuff; the doublet reads on
        ax0, ax1 = K.P(SLEEVE_R_SPEC["base"]), K.P(WR)
        belt_clip = belt_clip.intersection(K.halfplane(ax0, ax1, side=+1 if K.halfplane(ax0, ax1, side=+1).contains(
            K.Point(300.0, 440.0)) else -1))
    # the reed stalk runs on under the hands and arms; a run showing between
    # them shorter than 20 px is dropped (no stray white hook), and a node is
    # whole or hidden under a hand or a forearm (never a paper 'C')
    # (round 2) the stalk runs on from node to node and passes under the loom
    # forearm, so the right half reads as one continuous reed (the r1 skip circle
    # r 40 round the buckle and the short-run rule left a single isolated link);
    # the short run between the husk and the first node is left out (it would
    # leave the husk exactly at its pointed tip); a node half under the husk is
    # dropped like one half under a hand
    husk_x1 = husk.shape.bounds[2]
    bl = B.reed_belt(belt_clip, y=BELT_Y, h=24.0, sag=4.0, x0=220.0, x1=560.0, front=358.0, rise=BELT_RISE,
                     node_every=BELT_NODES[0], node_phase=BELT_NODES[1],
                     skip=K.box(husk.shape.bounds[0] - 12.0, 400.0, husk_x1 + 10.0, 490.0),
                     avoid=K.U(arm_front, husk.shape), cover=K.U(arm_front, husk.shape), min_run=20.0)

    # ---- sleeves (behind the body): puffed, comb sprays in Aquifer -----------------
    arm_l = B.region([(266, 322), (224, 323), (185, 341), (163, 378), (159, 414), (170, 445)],
                     ("L", [(170, 445), (248, 452)]), [(248, 452), (249, 420), (253, 370), (266, 322)])
    sc.part("armL", B.sleeve_part(arm_l, SLEEVE_L, ink=True, avoid=K.U(torso, arm_front)))
    # (round 3) the far arm's inner edge runs wholly behind the doublet (x ≤ its
    # edge): the r2 edge bowed out to x 537.5 near the band, leaving a 0.5 px
    # crack between the doublet and the loom that the silhouette stroked as a
    # 6 px ink tab on the loom's left contour (y 500–511)
    arm_r = B.region([(508, 316), (552, 318), (586, 342), (601, 384), (600, 440), (592, 530)],
                     ("L", [(592, 530), (530, 530)]), ARM_R_INNER)
    sc.part("armR", B.sleeve_part(arm_r, SLEEVE_R, ink=True, avoid=K.U(torso, arm_front)))

    # ---- body: the jade doublet, the red jerkin, its gold guards, the belt ----------
    dp = B.comb_ink(torso, DOUBLET_SPRAYS, pitch=8.0, tick=10.0, angle=52.0,
                    avoid=K.U(jer, bl.shape, arm_front)) if DOUBLET_SPRAYS else None
    sc.add("doublet", K.fill(torso, K.JADE) + (dp or K.C.Frag()) + K.outline(torso), torso)
    # the guards are gold braid (solid gold with an Aquifer contour and
    # rungs: the only legal gold on red, §C.4)
    g_parts = [B.ladder_guard(e_l, 15.0, side=-1, extend=(8.0, 0.0), color=K.GOLD,
                              clip=guard_stop(e_l, -1, 15.0, (8.0, 0.0), husk.shape, jer)),
               B.ladder_guard(e_r, 15.0, side=+1, extend=(8.0, 0.0), color=K.GOLD,
                              clip=guard_stop(e_r, +1, 15.0, (8.0, 0.0), husk.shape, jer)),
               B.ladder_guard(s_l, 14.0, side=+1, extend=(0.0, 8.0), clip=jer, node_every=0, color=K.GOLD),
               B.ladder_guard(s_r, 14.0, side=-1, extend=(0.0, 8.0), clip=jer, node_every=0, color=K.GOLD)]
    # the jerkin's red is left plain: the reed / comb-spray work is carried in
    # Aquifer on the jade and gold (§C.4: nothing drawn in Aquifer on red)
    sc.add("jerkin", K.fill(jer, K.RED) + K.outline(jer), jer)
    for k, g in enumerate(g_parts):
        sc.part(f"guard{k}", g)
    sc.part("belt", bl)

    # ---- head -------------------------------------------------------------------
    sc.part("hair", H.pageboy(outer=[(446, 170), (474, 192), (486, 228), (485, 266), (476, 298), (454, 318)],
                              inner=[(420, 320), (396, 300), (392, 262), (398, 226), (412, 190), (430, 172),
                                     (446, 170)], n=4, ends=HAIR_ENDS, curl_deg=120.0))
    sc.part("lockF", H.far_lock(outer=[(334.0, 181.0), (315.0, 200.0), (310.0, 226.0), (318.0, 250.0),
                                       (340.0, 266.0)],
                                inner=[(364.0, 268.0), (358.0, 232.0), (354.0, 190.0), (334.0, 181.0)],
                                n=2, first=8.5, ends=[70.0, 56.0], curl_deg=110.0))
    sc.part("neck", K.neck(fc, bottom=312.0, width=33.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("collar", J.standing_collar(**COLLAR))
    sc.part("ear", J.ear(fc))
    sc.part("cap", J.bonnet(**CAP))
    # the heron plume, pinned on the cap's side by the club brooch
    vane, quill = H.heron_plume3(PLUME, **PLUME_KW)
    sc.part("plume", vane)
    sc.part("quill", quill)
    sc.part("brooch", J.club_brooch(BROOCH, **BROOCH_KW))
    sc.part("clasp", K.lion_clasp(CLASP, 40.0))
    sc.part("buckle", husk)
    # gold buttons on the vee's midline (the vee narrows to the buckle)
    for k, (x, y) in enumerate(BUTTONS):
        c = K.circle((x, y), 6.3)
        sc.add(f"button{k}", K.fill(c, K.GOLD) + K.outline(c, K.FINE), K.R(c).buffer(K.FINE / 2), sil=False)

    # ---- arms, paddle, hands -------------------------------------------------------
    sprayL = FOREARM_L_SPRAY
    if ARM_L is not None:
        E, Wc = K.P(ARM_L["elbow"]), (K.P(cuffL.meta["inner_edge"][0]) + K.P(cuffL.meta["inner_edge"][1])) / 2
        uu = (Wc - E) / float(np.hypot(*(Wc - E)))
        a0, a1 = E + uu * ARM_L.get("spray", (6.0, 26.0))[0], Wc - uu * ARM_L.get("spray", (6.0, 26.0))[1]
        sprayL = f"M{a0[0]:.2f} {a0[1]:.2f}L{a1[0]:.2f} {a1[1]:.2f}"
    sc.part("forearmL", B.sleeve_part(fl, [sprayL], ink=True, avoid=K.U(cuffL.shape, hands)))
    if FOREARM_R_SPRAY:
        slR = B.sleeve_part(slR.shape, [FOREARM_R_SPRAY], ink=True, avoid=K.U(cfR.shape, hands,
                                                                               paddle.shape.buffer(K.HALO)))
    sc.part("sleeveR", slR)
    sc.part("paddle", paddle, halo=K.HALO, halo_only=("jerkin", "armR", "doublet"))
    sc.part("cuffR", cfR)
    sc.part("cuffL", cuffL)
    handL.add_to(sc, "handL", halo=0.0)
    handR.add_to(sc, "handR", halo=0.0)
    if DROP_HEEL_POCKET:
        # the kit's heel pocket (ground between the heel, the cuff and the
        # loom's channel turned to paper) lands below the belt here, as a
        # detached paper patch between the forearm and the loom: drop it
        sc.items = [it for it in sc.items if "~heel~" not in it.name]
    return sc


def build():
    return figure().layers()
