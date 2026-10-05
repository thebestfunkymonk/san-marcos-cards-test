"""art/KC.py — K♣ · The Cypress King (House of the Reed), creative brief §H.7.

The elder of the banks, as long-lived as a bald cypress. Built with
deck.courtkit (the hand every court shares) plus the K♣ parts in
art/_kc_crown.py, _kc_bird.py, _kc_robe.py, _kc_regalia.py and _kc_parts.py.

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
    hair        gold     two lock fans beside the face, 4 ribbons (3 current lines)
    beard       gold     two-pointed, of flat comb sprays (§H.7): each lobe a one-sided
                         spray whose rachis follows the outer edge and whose teeth
                         sweep down and in to the point; tips (358 / 392, ≈ 337)
    moustache   gold     two drooping leaves (§H.0 kit)
    robe        jade     neckline 272; shoulders to the corner (≈ 180, 330); sides
                         flaring out in a concave arc to the band (a cypress's
                         buttressed base); 30 px plain border + FINE seam; buttress
                         fluting in Aquifer: rays from (375, −300), 13 px apart at the
                         band, new flutes forking off their outer neighbours as the
                         robe widens (no free ends)
    stole       red      x 298–360 each side, over the shoulders from behind the neck;
                         knocked out: a piping line 5.6 px inside the edge and a column
                         of cypress sprigs at y 396 / 444 / 492 (§G.18 comb sprays at
                         MEDIUM, tilted, each with its round cone)
    collar      gold     the collar of office (§H.7 'a gold comb-spray collar'): cone
                         beads and comb-spray links on one arc through (250, 292),
                         (375, 366), clipped to the robe
    clasp       gold     the Lion Mark, 40 px, (375, 372) (§H.0, never a halo)
    orb         gold     a bald-cypress cone (§H.7): (300, 414) r 40, held from below
                         (cup hand, grip 0.62). Scales = a spherical Voronoi of whorls
                         round the stalk (1 / 5 / 6 / 5 / 1: smaller toward the poles),
                         seen from above the stalk and turned so it rises at the upper
                         left; MEDIUM seams crinkled into slow S's, the limb bulging
                         3 px per rim scale; each lit scale an Ø3.4 umbo with up to three
                         FINE wrinkle arcs springing from it; the right hemisphere's
                         scales half-hatched whole; the stalk a leaning CONTOUR stub
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
    arms        red      forearms from the band (222 / 496, 550) to the wrists
                         (268, 482) / (508, 446), jade cuffs
    hands       paper    cup under the cone (wrist down-left); fist on the staff
                         at (540, 404), gripped from the body side
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

AX = K.AX
HEAD = (AX, 207.0)
ORB_C, ORB_R = (300.0, 414.0), 40.0
FIST = (540.0, 404.0)
FIST_H = 38.0
STAFF_X = 540.0

ROBE = dict(neck_y=258.0, run=132.0, neck_heading=172.0, flare=8.0, side_heading=93.0, border=34.0, flute_kind="strata",
            flute_kw=dict(vy=-400.0, widths=(34.0, 10.0), centre=30.0))
COLLAR = dict(link_w=18.0, bead_r=8.4, link_len=30.0, centre_gap=13.0)   # the first beads run in behind the clasp
STOLE = dict(x_in=362.0, x_out=291.0, shoulder=(266.0, 292.0), piping_sides="outer",
             sprays=(396.0, 444.0, 492.0))
BEARD = dict(n=2, pitch=15.0, tick=6.0, tick_angle=40.0)
CROWN = dict(H=64.0, widths=(34.0, 38.0, 44.0, 38.0, 34.0), xs=(-60.0, -31.0, 0.0, 31.0, 60.0), knob=0.24,
             side_k=1.8, order="front", flute_mode="half", half_joint=False, centre_mode="one", hatch_phase=(2.0, 3.0), band_hw=78.0,
             wave_top=(26.0, 2.6), ripple=(2, 26.0, 2.2))
BIRD = dict(wing=((10.0, -46.0), (-2.0, -39.0), (-5.0, -25.0), (0.0, -10.0), (22.0, 9.0), (22.5, -14.0),
                             (19.5, -34.0), (15.0, -45.0)),
            tail=((9.0, -8.0), (20.0, -14.0), (30.0, 10.0), (20.0, 15.0)), collar=(-62.0, -51.0), belt_y=(-47.5, -37.0),
            vent=((-2.0, -6.0), (12.0, -12.0), (24.0, 8.0), (14.0, 8.0), (6.0, 3.0)))
STAFF = dict(top=198.5, hw=12.0, collars=(198.5, 300.0, 474.0), collar_hw=16.0, flute_dx=3.45)
GRIP = 0.62
ORB = dict(rings=RG.CONE_WHORLS, jitter=5.0, spin=0.0, tilt=-38.0, roll=30.0, crinkle=1.2, bulge=3.0, umbo_d=3.4,
           wrinkles=3, hatch_side=1, term_lon=25.0, stem=(-1.5, 9.0), stem_lean=-12.0)
FACE = dict(lids="heavy", lid_sag=3.6, pupil_tuck=-1.8, brow_drop=4.0, brow_sag=2.8, brow_out=37.0, nose_bot_dy=23.0)


def figure(opts=None):
    o = opts or {}
    sc = K.Scene(rank="K")
    # heavy-lidded and sage (§H.7): the lids lowered (a downcast, inward gaze),
    # the brows long and drooping at their outer ends, a longer nose
    fc = K.face(HEAD, "frontal", age="elder", **{**FACE, **o.get("face", {})})

    # ---- body, back to front ----------------------------------------------------
    rb = RB.robe(**{**ROBE, **o.get("robe", {})})
    sc.part("robe", rb)
    for side in (-1, 1):
        sc.part(f"stole{side}", RB.stole(side, within=rb.shape, **{**STOLE, **o.get("stole", {})}))
    sc.part("collar", KP.spray_collar(within=rb.shape, **{**COLLAR, **o.get("collar", {})}))
    sc.part("clasp", K.lion_clasp((AX, 372.0), 40.0))

    # ---- head ---------------------------------------------------------------------
    hs = K.HairSpec(**{**dict(top=(-52.0, -30.0), bulge=(-64.0, 40.0), bottom=(-53.0, 110.0), ribbons=4),
                       **o.get("hair", {})})
    for side in (-1, 1):
        sc.part(f"hair{side}", K.hair_fall(fc, side, hs))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    mo = K.moustache(fc, K.MoustacheSpec(**{**dict(root=(-1.5, 8.5), tip=(-32.0, 30.0), arch=7.0),
                                           **o.get("moustache", {})}))
    sc.part("beard", KB.spray_lines_beard(fc, mo, **{**BEARD, **o.get("beard", {})}))
    sc.part("moustache", mo)
    sc.part("crown", CR.knee_crown(**{**CROWN, **o.get("crown", {})}))

    # ---- arms and attributes ------------------------------------------------------
    WL, WR = (268.0, 482.0), (508.0, 446.0)
    slL, cfL = K.sleeve(K.SleeveSpec(base=(222.0, 552.0), wrist=WL, sag=6.0, width=66.0, wrist_w=38.0, cuff=14.0, folds=0,
                                     color=K.RED, cuff_color=K.JADE))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(496.0, 548.0), wrist=WR, sag=-7.0, width=68.0, wrist_w=40.0, cuff=14.0, folds=0,
                                     color=K.RED, cuff_color=K.JADE))
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    sc.part("staff", RG.gold_staff(x=STAFF_X, **{**STAFF, **o.get("staff", {})}), halo=K.HALO, halo_only=("robe",))
    sc.part("finial", BD.kingfisher3((STAFF_X, 176.0), **{**BIRD, **o.get("bird", {})}))
    orb_r = o.get("orb_r", ORB_R)
    orb = RG.cone_orb6(ORB_C, orb_r, **{**ORB, **o.get("orb", {})})
    sc.part("orb", orb)
    if orb.meta.get("stem") is not None:
        sc.part("orbstem", orb.meta["stem"], sil=False)
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    K.cup(ORB_C, orb_r, side=+1, wrist=WL, wrist_w=26.0, grip=o.get("grip", GRIP)).add_to(sc, "handL", halo=0.0)
    K.fist(FIST, -90.0, back=-1, wrist=WR, wrist_w=28.0, h=FIST_H).add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "K")
    return sc


def build():
    return figure().layers()
