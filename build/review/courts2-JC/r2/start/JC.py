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
| plume     | paper  | great-blue-heron plume: S from the brooch up and back, round terminal at (522, 78) — ≥ 12 px inside the gold rule, clear of the paddle; 2 current lines (the outer one rolls down past the inner one's end; neither touches), gold quill |
| hair      | gold   | page-boy bob, 4 current lines (ends staggered 168/152/118/98); far lock under the brim |
| collar    | jade   | short standing collar round the neck (top 286–296, foot 310–321) |
| clasp     | gold   | Lion Mark 40 px at (370, 340), on the doublet front |
| doublet   | jade   | the bust, showing at the sides and the front opening; its puffed sleeves carry §G.18 comb sprays in Aquifer |
| jerkin    | red    | sleeveless and waisted (armholes in to x 278 at the waist; the near one's edge runs on hidden under the loom wrist and forearm from y 428): plain Gill Red — no motif on the red (§C.4) |
| guards    | gold   | §G.19 reed-ladder braid down the front opening to the buckle |
| belt      | jade   | reed stalk knocked out, nodes every 54 px (whole or hidden); pecan-husk buckle (gold) at (358, 444); runs on behind the loom forearm and ends there |
| paddle    | jade/gold | upright like a halberd at x 548, blade tip y 100, half-hatched, gold band |
| forearms  | jade   | one comb spray each, elbow → wrist; red cuffs. Viewer's left: elbow at the belt, cuff 251–264 flush with the forearm; viewer's right: from below the band to the wrist at bend 40° / 0.9 (courtkit.fist_wrist), crossing the jerkin's edge, which runs on hidden under it |
| hands     | paper  | the squire's right hand resting on the belt, back to us (courtkit.flat via _jc_hands.belt_hand: 58 × 33, thumb opened 46° with a web crease, fingers softly curled, cut exactly on the cuff's edge); his left fist on the loom at (548, 404), from the body side (palm view) |
"""
from __future__ import annotations

import os
import sys

import numpy as np
from shapely.geometry import Point

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K  # noqa: E402
import _jc_body as B  # noqa: E402
import _jc_hands as JH  # noqa: E402
import _jc_head as H  # noqa: E402
import _jc_paddle as PD  # noqa: E402
import _jc_parts as J  # noqa: E402

HEAD = (385.0, 207.0)
PADDLE_X = 548.0
FIST = (548.0, 404.0)
FIST_KW = dict(shaft_w=22.0, back=-1, h=36.0)
WL = (263.0, 440.0)
# the squire's right hand resting on the belt (courtkit.flat via _jc_hands.belt_hand)
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
# reed nodes every 54 px from the buckle: both stay whole between the buckle
# and the loom forearm (58 put the second one half under the forearm)
BELT_NODES = (54.0, 0.0)

# the flat cap and its plume. The plume is pinned by the club brooch on the
# cap's side and streams back in an S; its round tip stays ≥ 12 px inside the
# gold rule (and far from the top-right chamfer) and clear of the paddle blade
CAP = dict(roll_c=(388.0, 174.0), roll_r=(50.0, 7.0), roll_h=14.0, crown_c=(398.0, 147.0), crown_r=(68.0, 19.0),
           crown_rot=-2.0)
BROOCH = (448.0, 164.0)
BROOCH_KW = dict(r=12.5, u=12.0, dy=0.0)
PLUME = [(448, 164), (457, 140), (462, 116), (476, 97), (497, 86), (522, 78)]
PLUME_KW = dict(w_max=28.0, w_root=11.0, quill=34.0, quill_w=11.0, quill_back=4.0, swell=0.42, tip_pow=0.8,
                vane_from=24.0, tip_r=4.5, bulb=1.8,
                lines=((2.8, 34.0, -40.0, -1), (-4.6, 38.0, -62.0, 0)), curl_deg=90.0)
COLLAR = dict(top=((344.0, 289.0), (414.0, 286.0)), top_sag=-7.0, foot=((338.0, 314.0), (420.0, 310.0)),
              foot_sag=-7.0)
CLASP = (370.0, 340.0)
BUTTONS = ((363.5, 372.0), (361.2, 396.0))

# the body: the jade doublet (the whole bust) under a sleeveless, waisted red
# jerkin whose front opening is edged with gold reed-ladder braid
TORSO = ([(342, 301), (300, 310), (266, 322), (244, 340)], [(244, 340), (246, 420), (244, 530)],
         ("L", [(244, 530), (536, 530)]), [(536, 530), (538, 420), (536, 340)],
         [(536, 340), (512, 322), (466, 308), (418, 300)], ("L", [(418, 300), (342, 301)]))
# the jerkin's near (viewer's-right) armhole edge below y 390 runs hidden under
# the loom hand's wrist, cuff and forearm (JERK_R_LOW), so it emerges only
# above the hand, meeting the back of the wrist square
JERK_R_LOW = [(512, 540), (510, 470), (504, 428)]


def jerk():
    return ([(342, 301), (304, 306), (276, 316)], [(276, 316), (268, 346), (272, 390), (278, 428), (272, 470), (260, 540)],
            ("L", [(260, 540), (512, 540)]), JERK_R_LOW + [(500, 390), (506, 346), (500, 314)],
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
FOREARM_L = ([(204, 434), (258, 424)], ("L", [(258, 424), (258, 456)]),
             [(258, 456), (220, 480), (196, 482), (180, 466), (182, 446), (204, 434)])
FOREARM_L_SPRAY = "M198 458L244 443"
CUFF_L = ((251.5, 424.5), (252.5, 457.5), 12.0)
SLEEVE_R_SPEC = dict(base=(476.0, 552.0), sag=-3.0, width=50.0, wrist_w=32.0, cuff=12.0)
FOREARM_R_SPRAY = "M490 506L503 458"


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
HAND_L2 = None          # dict(angle=, lead=, sweep_r=, hide=bool, **flat kw) for _jc_hands.rest_hand


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
    bl = B.reed_belt(belt_clip, y=BELT_Y, h=24.0, sag=4.0, x0=220.0, x1=560.0, front=358.0, rise=BELT_RISE,
                     node_every=BELT_NODES[0], node_phase=BELT_NODES[1],
                     skip=K.circle(BUCKLE, 40.0), avoid=arm_front,
                     cover=K.U(arm_front, husk.shape.buffer(4.0)), min_run=20.0)

    # ---- sleeves (behind the body): puffed, comb sprays in Aquifer -----------------
    arm_l = B.region([(266, 322), (224, 323), (185, 341), (163, 378), (159, 414), (170, 445)],
                     ("L", [(170, 445), (248, 452)]), [(248, 452), (249, 420), (253, 370), (266, 322)])
    sc.part("armL", B.sleeve_part(arm_l, SLEEVE_L, ink=True, avoid=K.U(torso, arm_front)))
    arm_r = B.region([(508, 316), (552, 318), (586, 342), (601, 384), (600, 440), (592, 530)],
                     ("L", [(592, 530), (534, 530)]), [(534, 530), (540, 440), (532, 370), (508, 316)])
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
