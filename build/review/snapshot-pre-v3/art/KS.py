"""art/KS.py — K♠ · The King Beneath (creative brief §H.1), built with deck.courtkit.

The deck's style test and the worked example of deck/COURT_GUIDE.md: every
part below is a courtkit builder with K♠ parameters; nothing is hand-placed
path data. The orb, the orb hand and two clean-ups at the sceptre hand are
refined locally in art/_ks_hands.py, from the kit's own primitives (the kit is
shared by all twelve courts). Read it top to bottom with the guide open.

Composition plan (card px; the TOP half only — art window x 139–611, y 55–511):

    part        colour   geometry (brief)
    ----------  -------  -------------------------------------------------------------
    crown       gold     Escarpment Crown (§H.1): band 154–180, ends on rays from
                         (375, 700); five merlons on the same rays, tops 128 / 105 / 82
                         (three fault-steps); side merlons half-hatched on their outer
                         halves, the centre merlon's lower course chevron-hatched about
                         the axis; brow jewel r 13, red Ø8.4 core; four studs. x 302–448
    head        paper    egg r 44 about (375, 207): 88 × 113.8, top 163, chin 277 (§H.0)
    face        ink      12 strokes: eyes y 213 at x 353 / 397, 24 × 10.1, RULE lids,
                         Ø6 pupils hanging from the lids; brows y 201; nose ridges
                         216–231 with alar wings; lip bow y 255.5 under the moustache,
                         lower-lip tick y 263
    hair        gold     two lock fans (outer arc through (323,177), (310,247),
                         (321,315)), 4 ribbons: 3 current lines rolling into terminals
    beard       gold     forked: sideburn (334,227), bulge (334,279), tips (360/390, 331),
                         notch 302; 3 current lines per lobe converging on the tips
    moustache   gold     two drooping leaves, (373.5, 242.5) → (345, 259)
    collar      red      standing fan collar behind the head (§H.1 'collar lining: Gill
                         Red'), jade turned rim, pointed corners (265 / 485, 236); its
                         foot hides under the mantle's neckline
    mantle      jade     neckline 270 on the axis, shoulders to the corner (182, 330)
                         (§H.0: ≈ 330), sides to x 145 at the band; 54 px plain border
                         + FINE seam; strata 12/19 (thin courses hatched) with ONE
                         straight Balcones fault (205, 470) → (290, 300), steep across
                         the left chest, the courses right of it dropped one course
    tunic       paper    Spring Lake lens (throat 312, half-width 33 at y 525) with
                         karst voids; the Ø10 and Ø16 caverns flooded jade (the aquifer)
    lapels      red      shawl lapels on the lens arcs, 68 wide at the waist, from
                         x 294 on the neckline; rising bubbles (Ø4.2 → 9.5) knocked out
                         of the right lapel (the left one's column would run behind the
                         orb and its hand: its one visible dot paired with the orb's
                         bubble); the right lapel's edge tucks into the forearm's cuff
                         on a 6 px round (no acute jade tip, no unlined red on jade)
    clasp       gold     the Lion Mark, 40 px, solid gold + Aquifer contour, (375, 358): the kit's
                         K.lion_clasp (director's note): the A♠ face at 1/4 — two level
                         almond eyes, solid trapezoid nose on a level mouth — 12 pointed locks,
                         and wide level wings of three primaries each
    orb         gold     (300, 424) r 33 (§H.1: ≈ 300, 430), three ripple latitudes
                         (gaps 8.2 / 10.6 / 20: the lowest runs behind the fingers, never
                         along their tips), one free bubble above the pole; held from
                         below (cup hand)
    sceptre     gold     x 540, 22 wide, seven segments (marl / strata / chert) between
                         raised collars, knop, finial rosette (540, 114) r 29 with a
                         red centre; a 4.3 px paper halo where it crosses the mantle;
                         the strata course that lay along the top of the fist dropped
    arms        red      forearms rise from the band (222 / 472, 550) to the wrists
                         (276, 479) / (498, 455), jade cuffs; C2-paired they cross
                         the band as one diagonal each side (the pinwheel)
    hands       paper    the king's RIGHT hand under the orb, back to the viewer
                         (_ks_hands.orb_cup): four fingers 10 wide curl up the orb's
                         front to ≈ 430, three finger lines; the thumb leaves the back
                         low on the wrist side and rises to a round tip on the rim at
                         13° below the equator, a V open to the index; the back tapers
                         into the cuff (little-finger edge a cubic off the finger's
                         tangent). Fist on the sceptre at (540, 419), gripped from the
                         body side and so seen from the palm (the king's LEFT hand,
                         hand='L')

Colour balance (deck.qa §C.2, both halves, band excluded): paper 45.2, jade 14.4,
red 12.6, gold 10.3, ink 17.5 — the ink includes the corner pip (2.4). (Before
the 2026-09 hand review: paper 45.1, jade 15.0, red 12.1; the forearm moved over
the right lapel in the kit round cost the jade.)
"""
from __future__ import annotations

from deck import courtkit as K
from art import _ks_hands as H

AX = K.AX
HEAD = (AX, 207.0)
ORB_C, ORB_R = (300.0, 424.0), 33.0
FIST = (540.0, 419.0)                          # on the collar at y 435.6: the fist covers a joint, not a chert tip
FAULT = ((205.0, 470.0), (290.0, 300.0))      # one straight Balcones fault, steep across the left chest
CUP_WRIST = (276.0, 479.0)                     # ≈ 1.6 r below the orb: the cup's back no longer than its fingers
ORB_GAPS = (8.2, 10.6, 20.0)                   # the lowest ripple runs behind the fingers, never along their tips


def _tuck_lapel(lp, front, r=6.0):
    """The lapel with the acute jade tip left between its edge and the forearm
    in front (sleeve + cuff: their edges converge at ≈ 20°) filled in red, closing
    on a round arc of radius ``r`` — so the lapel's edge line turns into the
    cuff instead of heal trimming it back and leaving red on jade unlined."""
    both = K.U(lp.shape, front)
    tip = both.buffer(r, quad_segs=12).buffer(-r, quad_segs=12).difference(both)
    tip = K.U(*[g for g in K._polys_of(tip) if g.area > 2.0 and g.distance(lp.shape) < 0.5
                and g.distance(front) < 0.5])
    if tip.is_empty:
        return lp
    shape = K.U(lp.shape, tip.buffer(0.3, quad_segs=6).intersection(both.buffer(0.3).union(tip)))
    out = K.C.Frag()
    for m in lp.fills.marks:
        out += K.fill(K.U(K.G.to_shape(m.d, tol=0.05), tip.buffer(0.3, quad_segs=6)), K.RED)
    return K.Part(shape, out, K.outline(shape), lp.meta)


def figure():
    sc = K.Scene(rank="K")                     # rank: heal against the band rule and medallion clip
    fc = K.face(HEAD, "frontal", age="elder", lids="heavy")

    # ---- body, back to front ---------------------------------------------------
    sc.part("collar", K.standing_collar(top_y=236.0, half_w=110.0, neck_y=262.0, shoulder=(-112.0, 312.0),
                                        side_sag=-3.0, rim=10.5))
    ms = K.MantleSpec(neck_y=270.0, neck_heading=170.0, run=140.0, corner_r=30.0, side_heading=99.0)
    mant = K.mantle(ms, border=54.0, pattern_kind="strata", heights=(12.0, 19.0), hatched="thin", fault=FAULT,
                    y0=ms.neck_y)
    sc.part("mantle", mant)
    ls = K.LensSpec(lapel_w=68.0, half_w=33.0)
    sc.part("tunic", K.tunic(ls, pitch=(22.0, 16.5), weights=(0.12, 0.33, 0.55), flood_min=9.5))
    # the orb hand (art/_ks_hands.py): the kit's cup with a thumb that leaves the back low
    # on the wrist side and rises to a round tip on the rim, opening a V to the index;
    # the fingers reach higher up the orb, over its lowest ripple
    cup = H.orb_cup(ORB_C, ORB_R, wrist=CUP_WRIST, wrist_w=26.0, grip=0.40, thumb_tip=13.0, fw=10.0)
    # red forearms rise from the band to the wrists, jade cuffs; C2-paired they cross the
    # band as one diagonal (built here: the lapels tuck under them)
    WL, WR = CUP_WRIST, (498.0, 455.0)
    slL, cfL = K.sleeve(K.SleeveSpec(base=(222.0, 552.0), wrist=WL, sag=2.0, width=52.0, wrist_w=34.0, cuff=16.0,
                                     color=K.RED, cuff_color=K.JADE))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(472.0, 548.0), wrist=WR, sag=-4.0, width=52.0, wrist_w=36.0, cuff=16.0,
                                     color=K.RED, cuff_color=K.JADE))
    for side in (-1, 1):
        # the left lapel's bubble column runs behind the orb and the orb hand: its one
        # visible dot sat beside the orb's own bubble as a stray pair, so it has none
        lp = K.lapel(ls, side, mant.shape, shoulder_x=294.0, collar_sag=-4.0, bubbles=side > 0,
                     bub_top=384.0, bub_bottom=498.0, bub_max=9.5)
        if side > 0:
            lp = _tuck_lapel(lp, K.U(slR.shape, cfR.shape))
        sc.part(f"lapel{side}", lp)

    # ---- head ------------------------------------------------------------------
    hs = K.HairSpec(bulge=(-65.0, 40.0), bottom=(-54.0, 108.0), ribbons=4)
    for side in (-1, 1):
        sc.part(f"hair{side}", K.hair_fall(fc, side, hs))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    mo = K.moustache(fc, K.MoustacheSpec(root=(-1.5, 8.5), tip=(-30.0, 25.0), arch=6.2))
    sc.part("beard", K.beard(fc, K.BeardSpec(bulge=(-41.0, 72.0), tip=(-15.0, 124.0), notch_dy=95.0,
                                             stagger=13.0, lines=3), mo=mo))
    sc.part("moustache", mo)
    sc.part("crown", K.merlon_crown())
    sc.part("clasp", K.lion_clasp((AX, 358.0), 40.0))          # never a halo (§G.2)

    # ---- arms and attributes -----------------------------------------------------
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    # the king's LEFT hand, forearm from the body side: seen from the palm (fingers curled toward us)
    fist = K.fist(FIST, -90.0, back=-1, hand="L", wrist=WR, wrist_w=28.0, h=38.0)
    # the strata segment's top course lay along the top of the fist (one heavy ink band): dropped
    sc.part("sceptre", H.clear_grazing(K.sceptre(K.SceptreSpec(hw=11.0, collar_hw=14.5)), fist.hand.shape),
            halo=K.HALO, halo_only=("mantle",))
    sc.part("orb", H.orb(ORB_C, ORB_R, gaps=ORB_GAPS))
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    cup.add_to(sc, "handL", halo=0.0)
    fist.add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "K")                      # last: the medallion's mask keeps lines 3 px off the band
    return sc


def build():
    return figure().layers()
