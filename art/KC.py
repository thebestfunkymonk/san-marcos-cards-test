"""art/KC.py — K♣ · The Cypress King (House of the Reed), creative brief §H.7.

The elder of the banks, as long-lived as a bald cypress. Built with
deck.courtkit (the hand every court shares) plus the K♣ parts in
art/_kc_crown.py, _kc_bird.py, _kc_robe.py, _kc_regalia.py, _kc_parts.py,
_kc_hands.py (the cone hand; the fist's crease, curls and the staff's caps) and _kc_hair.py.

Composition plan (card px; the TOP half only — art window x 139–611, y 55–511):

    part        colour   geometry (brief)
    ----------  -------  -------------------------------------------------------------
    crown       gold     the Knee Crown (§H.7, §G.17): band 152–182 on the axis (hw 78,
                         bow 4, ends on rays from (375, 640)) of two ripple lines — the
                         water the knees stand in; five knees at heights 0.65 / 0.8 /
                         1.0 / 0.8 / 0.65 × 64, at x 315 / 344 / 375 / 406 / 435,
                         34–44 wide: rounded cones overlapping as knees grow (a clump,
                         the tallest in front); HALF-HATCHED like the K♠ merlons (FINE
                         45° at 7.0): each side knee on its outer half, the lines
                         square to its outer flank; the centre knee on its left half.
                         No joint line (a split knee reads as a feather or a leaf)
    head        paper    egg r 44 about (375, 207): 88 × 113.8, top 163, chin 277 (§H.0)
    face        ink      frontal, elder, heavy-lidded, sage: eyes y 213, RULE lids,
                         Ø6 pupils hanging from the lids
    hair        gold     two lock fans beside the face (outer edge through dx −54 / −66 /
                         −55), ONE current line each (_kc_hair): the visible band
                         beside the face and beard is ≈ 16 px, room for one line with
                         §I.12's paper; the kit's second line ran along the face edge
                         and heal cut the head outline at the temples
    beard       gold     two-pointed, of flat comb sprays (§H.7): each lobe a one-sided
                         spray whose rachis follows the outer edge and whose teeth
                         sweep down and in to the point; tips (358 / 392, ≈ 337)
    moustache   gold     two drooping leaves (§H.0 kit)
    robe        jade     neckline 272; shoulders to the corner (≈ 180, 330); sides
                         flaring out in a concave arc to the band (a cypress's
                         buttressed base); 34 px plain border + FINE seam; buttress
                         fluting in Aquifer: strata on rays from (375, −400), plain
                         ridges 34 / hatched grooves 10 at the band. Two grooves are
                         left out (skip 103/113, 191/201): the first ran up beside
                         each stole's outer edge into the collar's end at a shallow
                         angle (heal cut its flute tops into free ends), the second
                         pinched into the border seam. The ground on each forearm's
                         outer side (to the stole / the staff's halo) is plain
                         (_kc_robe.plain_pocket: a flute there forked off the sleeve's
                         contour and ran within 4.2 px of it)
    stole       red      x 298–360 each side, over the shoulders from behind the neck;
                         knocked out: a piping line 5.6 px inside the edge and a column
                         of cypress sprigs at y 396 / 444 / 492 (§G.18 comb sprays at
                         MEDIUM, tilted, each with its round cone); on the viewer's
                         left a sprig showing < 30 % beside the cone and its hand is
                         dropped whole (the 444 one: a lone tick at the limb)
    collar      gold     the collar of office (§H.7 'a gold comb-spray collar'): cone
                         beads and comb-spray links on one arc through (250, 292),
                         (375, 366), clipped to the robe
    clasp       gold     the Lion Mark, 40 px, (375, 372) (§H.0, never a halo)
    orb         gold     a bald-cypress cone (§H.7): (300, 414) r 40, held from below
                         (cup hand). Scales = a spherical Voronoi of whorls
                         round the stalk (1 / 5 / 6 / 5 / 1: smaller toward the poles),
                         seen from above the stalk and turned so it rises at the upper
                         left; MEDIUM seams crinkled into slow S's, the limb bulging
                         3 px per rim scale; each lit scale an Ø3.4 umbo with up to three
                         FINE wrinkle arcs springing from it; the right hemisphere's
                         scales half-hatched whole; the stalk a short gold peduncle
                         (7.4 → 9 wide, flat-ended, MEDIUM outline) leaning out from
                         behind the limb at the upper left (the bare CONTOUR stub read
                         as the fuse of a bomb). ORB_DROP: six seams that ran ALONG
                         the hand or the limb are left out (down the V beside the
                         thumb; down the little finger's edge and along the limb
                         under it, with its stub; along the top limb from the stalk;
                         the S-seam hugging the upper-right limb): each doubled an
                         edge into an ink knot with a gold hairline; the hatch line
                         lying along the lower-right limb goes too (hatch_limb)
    staff       gold     x 540, 24 wide, from the band to the top collar at 198.5; raised
                         bead collars (32 wide) at 198.5 / 300 / 474; two FINE Aquifer
                         flutes 3.45 either side of the axis, collar to collar (the
                         fluted cypress; gold like the K♠ sceptre, never a red-and-paper
                         stripe: that read as a candy cane)
    finial      gold     the wrought-gold belted kingfisher (§H.7): feet at (540, 176),
                         crest top ≈ 80, bill tip (482, 108), facing the king; paper
                         collar, jade breast belt, four chased breast bands below it,
                         two scalloped covert rows over three stepped primaries; the
                         toes grip a ball knop (r 10.5, FINE fillet) seated on the
                         staff's top collar
    arms        red      forearms from the band (222 / 440, 550) to the wrists
                         (269, 473) / (504, 431), jade cuffs; the left cuff 34 wide so
                         its corner stands 7 px off the stole's edge (at 38 it came
                         within 3 px and heal broke the stole's edge line); the right
                         forearm leans 29° (base 440: at 458 the wrist bent 32° and the
                         ground between sleeve and staff began as a 6 px jade tab)
    hands       paper    the king's RIGHT hand under the cone, back to the viewer
                         (_kc_hands.cone_cup, the K♠'s orb hand): four fingers 11.5
                         wide curl up the cone's front to ≈ 425, three finger lines
                         from the notches to the knuckles; the thumb leaves the back
                         low on the wrist side and rises to a round tip on the rim
                         20° below the equator, a V open to the index; the back
                         tapers into the cuff (little-finger edge a cubic); the tip's
                         centre 3.5 px OUT past the rim, so the limb meets the tip's
                         upper-right side and reads as passing behind it (at +1 the
                         limb ran into the apex); the V's bottom a 4 px fillet. The LEFT
                         hand a kit fist on the staff at (540, 404), gripped from the
                         body side and so seen from the palm (hand='L'); wrist
                         50° off the knuckle line at 0.85 × the block (a short wrist);
                         the thumb crease cut to the 22 px at its tip
                         (_kc_hands.short_crease: the full crease made thumb + index
                         read as a pointing finger) and joined into the top fingertip
                         curl, the lowest curl run onto the fist's bottom edge
                         (_kc_hands.tidy_fist: a knot and a free end); the staff's
                         lines cut 1 px outside the fist (_kc_hands.clear_caps: their
                         round caps showed as nubs on the fist's edges)

Colour balance (deck.qa §C.2, both halves, band excluded): paper 44.5, jade 14.5,
red 10.6, gold 12.5, ink 17.9 (≤ 19 ruling) — the ink includes the corner pip.
(Round 1 of this review: paper 44.5, jade 14.0, red 10.7, gold 12.3, ink 18.5.)
(Kit-round rebuild before this review: paper 44.8, jade 13.9, red 10.7, gold 12.2,
ink 18.4; the cone hand is smaller than the kit cup's 13.6 px fingers, the hair
2 px wider.)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deck import courtkit as K            # noqa: E402
from art import _kc_parts as KP           # noqa: E402
from art import _kc_crown as CR           # noqa: E402
from art import _kc_bird as BD            # noqa: E402
from art import _kc_robe as RB            # noqa: E402
from art import _kc_regalia as RG         # noqa: E402
from art import _kc_beard as KB           # noqa: E402
from art import _kc_hands as H            # noqa: E402
from art import _kc_hair as HR            # noqa: E402

AX = K.AX
HEAD = (AX, 207.0)
ORB_C, ORB_R = (300.0, 414.0), 40.0
FIST = (540.0, 404.0)
FIST_H = 38.0
FIST_KW = dict(shaft_w=24.0, back=-1, h=FIST_H)     # the staff is 24 wide
STAFF_X = 540.0

ROBE = dict(neck_y=258.0, run=132.0, neck_heading=172.0, flare=8.0, side_heading=93.0, border=34.0, flute_kind="strata",
            flute_kw=dict(vy=-400.0, widths=(34.0, 10.0), centre=30.0, shift={103.0: -2.0, 113.0: -4.0, 147.0: 2.5, 157.0: 2.5, 191.0: -6.0, 201.0: -6.0}))
GROOVE_IN, GROOVE_MID, GROOVE_OUT = 101.0, 149.5, 185.0     # inner bounds of the three side grooves (at y 511)
COLLAR = dict(link_w=18.0, bead_r=8.4, link_len=30.0, centre_gap=13.0)   # the first beads run in behind the clasp
STOLE = dict(x_in=362.0, x_out=291.0, shoulder=(266.0, 292.0), piping_sides="outer", keep_frac=0.3,
             sprays=(396.0, 444.0, 492.0))
HAIR = dict(top=(-54.0, -30.0), bulge=(-66.0, 40.0), bottom=(-55.0, 110.0), ribbons=4)
HAIR_KEEP = 1
BEARD = dict(n=2, pitch=15.0, tick=6.0, tick_angle=40.0)
CROWN = dict(H=64.0, widths=(34.0, 38.0, 44.0, 38.0, 34.0), xs=(-60.0, -31.0, 0.0, 31.0, 60.0), knob=0.24,
             side_k=1.8, order="front", flute_mode="half", half_joint=False, centre_mode="one", hatch_phase=(2.0, 3.0), band_hw=78.0,
             wave_top=(26.0, 2.6), ripple=(2, 26.0, 2.2))
BIRD = dict(wing=((10.0, -46.0), (-2.0, -39.0), (-5.0, -25.0), (0.0, -10.0), (22.0, 9.0), (22.5, -14.0),
                             (19.5, -34.0), (15.0, -45.0)),
            tail=((9.0, -8.0), (20.0, -14.0), (30.0, 10.0), (20.0, 15.0)), collar=(-62.0, -51.0), belt_y=(-47.5, -37.0),
            vent=((-2.0, -6.0), (12.0, -12.0), (24.0, 8.0), (14.0, 8.0), (6.0, 3.0)))
STAFF = dict(top=198.5, hw=12.0, collars=(198.5, 300.0, 474.0), collar_hw=16.0, flute_dx=3.45)
CUP_WRIST = (269.0, 473.0)
SLEEVE_L = dict(base=(222.0, 552.0), sag=6.0, width=66.0, wrist_w=34.0, cuff=14.0)
FIST_WRIST = dict(bend=50.0, dist=0.85)
FIST_HAND = dict(wrist_w=28.0)
CREASE = 22.0
HEEL_R = 6.0                           # the staff hand's heel: a concave arc off the fist's underside (_kc_hands.soft_heel)
SLEEVE_R = dict(base=(440.0, 548.0), sag=-2.0, width=56.0, wrist_w=36.0, cuff=14.0)
POCKETS = ("R",)
POCKET_FAR = (300.0, STAFF_X)          # the pockets run in under the stole's edge / the staff
CUP = dict(wrist_w=26.0, grip=0.40, fw=11.5, converge=0.84, thumb_tip=20.0, thumb_root=(-0.4, 0.12), thumb_rim=3.5,
           vee_r=4.0)
ORB = dict(rings=RG.CONE_WHORLS, jitter=5.0, spin=0.0, tilt=-38.0, roll=30.0, crinkle=1.2, bulge=3.0, umbo_d=3.4,
           wrinkles=3, hatch_side=1, term_lon=25.0, stem=(-2.0, 10.0), stem_lean=-12.0, stem_w=(7.4, 9.0),
           hatch_limb=6.8)
# the cone seams that ran along the hand or the limb (midpoints): down the V beside the thumb;
# down the little finger's outer edge; along the limb under it; the stub from its junction to
# the limb; along the top limb from the stalk (a gold hairline crescent: a doubled top edge);
# the S-seam hugging the upper-right limb among the hatch
ORB_DROP = ((270.0, 427.5), (328.2, 429.3), (326.6, 440.2), (331.7, 436.3), (285.2, 380.6), (331.1, 399.1))
FACE = dict(lids="heavy", lid_sag=3.6, pupil_tuck=-1.8, brow_drop=4.0, brow_sag=2.8, brow_out=37.0, nose_bot_dy=23.0)


def figure(opts=None):
    o = opts or {}
    sc = K.Scene(rank="K")
    # heavy-lidded and sage (§H.7): the lids lowered (a downcast, inward gaze),
    # the brows long and drooping at their outer ends, a longer nose
    fc = K.face(HEAD, "frontal", age="elder", **{**FACE, **o.get("face", {})})

    # the cone and the hand under it first: the viewer's-left stole keeps only the
    # sprigs that show whole beside them
    orb_r = o.get("orb_r", ORB_R)
    WL = tuple(o.get("wl", CUP_WRIST))
    cup = H.cone_cup(ORB_C, orb_r, wrist=WL, **{**CUP, **o.get("cup", {})})
    hug = o.get("hug", True)
    orb = RG.cone_orb6(ORB_C, orb_r, avoid=cup.hand.shape if hug else None,
                       drop_at=tuple(o.get("orb_drop", ORB_DROP)) if hug else (),
                       **{**ORB, **o.get("orb", {})})
    front_l = K.U(orb.shape, cup.hand.shape)
    if o.get("orb_caps", True):
        # the cone's lines cut 1 px outside the hand under it: the MEDIUM limb's round caps poked
        # ≈ 0.5–1 px into the hand's paper at the thumb tip and the little finger
        orb = H.clear_caps(orb, cup.hand.shape)

    # the forearms (placed below, in front): the cup's wrist ≈ 1.45 r below the cone (its back no
    # longer than the fingers); the staff hand's wrist out along its axis (courtkit.fist_wrist)
    WR = tuple(K.fist_wrist(FIST, -90.0, **{**FIST_WRIST, **o.get("fist_wrist", {})}, **FIST_KW))
    spL = {**SLEEVE_L, **o.get("sleeveL", {})}
    spR = {**SLEEVE_R, **o.get("sleeveR", {})}
    slL, cfL = K.sleeve(K.SleeveSpec(**spL, wrist=WL, folds=0, color=K.RED, cuff_color=K.JADE))
    slR, cfR = K.sleeve(K.SleeveSpec(**spR, wrist=WR, folds=0, color=K.RED, cuff_color=K.JADE))

    # the staff hand (palm view), built before the robe: the robe's grooves close clear of it
    fist = K.fist(FIST, -90.0, wrist=WR, hand="L", **{**FIST_HAND, **o.get("fist", {})}, **FIST_KW)   # palm view
    crease = o.get("crease", CREASE)
    if crease:
        fist = H.short_crease(fist, keep=crease)
    if o.get("tidy", True):
        fist = H.tidy_fist(fist)
    if o.get("seat", True):
        fist = H.seat_fingers(fist)
    heel_r = o.get("heel_r", HEEL_R)
    if heel_r:
        g = K.fist_geom(FIST, -90.0, **FIST_KW)
        fist = H.soft_heel(fist, corner=(FIST[0] - (g["a"] + K.PARALLEL_MIN), FIST[1] + g["y1"] + 0.4), r=heel_r)
    sc0 = K.Scene()                              # the fist as it will stand, tucked into the right cuff
    sc0.part("sleeveR", slR)
    sc0.part("cuffR", cfR)
    fist_now = fist.tucked(sc0).shape

    # ---- body, back to front ----------------------------------------------------
    rkw = {**ROBE, **o.get("robe", {})}
    rb0 = RB.robe(**{**rkw, "fluting": False})          # the robe's shape (the stoles and collar lie within it)
    stoles = {side: RB.stole(side, within=rb0.shape, hide=front_l if side < 0 else None, **{**STOLE, **o.get("stole", {})})
              for side in (-1, 1)}
    collar = KP.spray_collar(within=rb0.shape, **{**COLLAR, **o.get("collar", {})})
    fk = dict(rkw.get("flute_kw") or {})
    if o.get("rules", True):
        # each side groove fitted to what stands in front of it (_kc_robe.strata_fluting rules)
        clear = K.GAP + K.FINE / 2 + K.MEDIUM / 2          # 6.8: §I.12's 4.2 between a FINE and a MEDIUM line
        stem = orb.meta.get("stem")
        cone_l = K.U(orb.shape, cup.hand.shape, stem.shape if stem is not None else None)
        fk["rules"] = [
            # inner groove: it opens onto the stole's edge where its inner line would run along it,
            # starts below the collar's end link, and (left) ends above the cone and its stalk
            dict(side=1, groove=GROOVE_IN, mode="merge", line="a", obstacle=stoles[1].shape, need=clear),
            dict(side=1, groove=GROOVE_IN, mode="top", obstacle=collar.shape, ray_obstacle=stoles[1].shape, need=clear,
                 ray_need=K.GAP_MARK + K.FINE / 2 + K.MEDIUM / 2 + 0.2),
            dict(side=1, groove=GROOVE_IN, mode="land", obstacle=K.U(slR.shape, cfR.shape), phase=True,
                 corners=RB.corners_of(cfR.shape)),
            # middle groove: hatched right down to the left sleeve (its edge lies along the hatch); on
            # the right it closes on a hatch line landing on the back of the staff hand
            dict(side=-1, groove=GROOVE_MID, mode="fit", obstacle=K.U(slL.shape, cfL.shape), need=clear, phase=True),
            dict(side=-1, groove=GROOVE_MID, mode="land", obstacle=K.U(slL.shape, cfL.shape), phase=True,
                 corners=RB.corners_of(cfL.shape)),
            dict(side=1, groove=GROOVE_MID, mode="cut", line="a", obstacle=fist_now, need=clear, phase=True),
            # outer groove: closes where it narrows into the border seam
            dict(side=-1, groove=GROOVE_OUT, mode="drop", line="b"),
            dict(side=-1, groove=GROOVE_OUT, mode="cut", line="a", obstacle="seam", need=K.GAP + K.FINE + 0.1),
        ]
        # the inner groove on the left would show only as a stub between the collar, the stole and
        # the cone's stalk; the outer groove on the right lies under the staff (a sliver of it
        # showed between the staff's halo and the border seam below the lowest collar)
        fk["side_skip"] = {-1: (GROOVE_IN, GROOVE_IN + 8.0), 1: (GROOVE_OUT, GROOVE_OUT + 10.0)}
    rkw["flute_kw"] = fk
    rb = RB.robe(**rkw)
    pk = o.get("pockets", POCKETS) or ()
    if pk:
        # the robe ground between the right forearm and the staff's halo stays plain: a sliver of
        # the middle groove there converged on the halo's paper edge
        zs = []
        if "L" in pk:
            zs.append(RB.sleeve_pocket(spL, slL.meta, POCKET_FAR[0]))
        if "R" in pk:
            zs.append(RB.sleeve_pocket(spR, slR.meta, POCKET_FAR[1]))
        rb = RB.plain_pocket(rb, K.U(*zs))
    sc.part("robe", rb)
    for side in (-1, 1):
        sc.part(f"stole{side}", stoles[side])
    sc.part("collar", collar)
    sc.part("clasp", K.lion_clasp((AX, 372.0), 40.0))

    # ---- head ---------------------------------------------------------------------
    hs = K.HairSpec(**{**HAIR, **o.get("hair", {})})
    for side in (-1, 1):
        sc.part(f"hair{side}", HR.hair_fall_clear(fc, side, hs, keep=o.get("hair_keep", HAIR_KEEP)))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    mo = K.moustache(fc, K.MoustacheSpec(**{**dict(root=(-1.5, 8.5), tip=(-32.0, 30.0), arch=7.0),
                                           **o.get("moustache", {})}))
    sc.part("beard", KB.spray_lines_beard(fc, mo, **{**BEARD, **o.get("beard", {})}))
    sc.part("moustache", mo)
    sc.part("crown", CR.knee_crown(**{**CROWN, **o.get("crown", {})}))

    # ---- arms and attributes ------------------------------------------------------
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    staff = RG.gold_staff(x=STAFF_X, **{**STAFF, **o.get("staff", {})})
    if o.get("caps", True):
        staff = H.clear_caps(staff, K.U(fist.hand.shape, fist.thumb.shape))
    sc.part("staff", staff, halo=K.HALO, halo_only=("robe",))
    if o.get("tuck", True):
        # the border seam runs on under the staff's paper halo: its end cap is centred ON the
        # halo's edge (the halo cuts lines behind a cap's width short of it, and where the seam
        # meets the halo's curved flank at a slant its cap stood clear of the paper)
        sc.add("seamtuck", RB.tuck_ends(rb, staff.shape.buffer(K.HALO + K.MEDIUM / 2, quad_segs=12)), sil=False)
    sc.part("finial", BD.kingfisher3((STAFF_X, 176.0), **{**BIRD, **o.get("bird", {})}))
    if orb.meta.get("stem") is not None:
        sc.part("orbstem", orb.meta["stem"], sil=False)     # behind the cone: it leaves the limb
    sc.part("orb", orb)
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    cup.add_to(sc, "handL", halo=0.0)
    fist.add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "K")
    return sc


def build():
    return figure().layers()
