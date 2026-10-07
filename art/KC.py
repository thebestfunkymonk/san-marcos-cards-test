"""K♣ · The Cypress King (House of the Reed), creative brief §H.7: continuous double-head, two cloak-sleeve hands.

The elder of the banks, as long-lived as a bald cypress. The whole-card textiles (art/_kc_garments.py) are
C2 about the card centre: the jade barrel robe (hatched border, FINE seam, plain-edged buttress ridges with
paper bark slits between hatched grooves, all following one stave scale) and the two red stole columns
(piping and knocked-out cypress sprigs) run from one figure's shoulders to the other's, so the seam (SEAM,
a gentle diagonal through the robe) is only a place where the 180° copy takes over: no band, medallion or
divider.

Hands (both ``K.hand5``, back view, posed by parameters):
  * the king's LEFT hand (viewer's right) wraps the gold cypress staff under the kingfisher finial;
  * the king's RIGHT hand (viewer's left) holds the cypress cone by its gilt stalk, the cone hanging below.
Each wrist continues a short jade sleeve that opens from the robe's outer edge, so the robe outline is the
sleeve's far end and its cuff mouth is the turn-back beside the hand.

Head, crown, beard, collar and finial are the K♣ parts of art/_kc_*.py (unchanged):
    crown     gold   the Knee Crown (§H.7, §G.17): five rounded cypress knees at 0.65/0.8/1/0.8/0.65 × 64
                     on a two-ripple band, half-hatched
    face      ink    frontal, elder, heavy-lidded, sage
    beard     gold   two-pointed, of flat comb sprays
    collar    gold   the collar of office: cone beads and comb-spray links on one arc
    clasp     gold   the Lion Mark, 40 px
    finial    gold   the wrought-gold belted kingfisher on a ball knop (§H.7)
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck import frames as F
from art import _kc_garments as KG
from art import _kc_parts as KP
from art import _kc_crown as CR
from art import _kc_bird as BD
from art import _kc_regalia as RG
from art import _kc_beard as KB
from art import _kc_hair as HR

DOUBLE_HEAD = "continuous"
SEAM = 8.0
AX = K.AX
HEAD = (AX, 207.0)
HAND_SCALE = 0.82

SX = 524.0                                     # staff axis
STAFF_TOP, STAFF_BOTTOM = 198.5, 444.0
GRIP = (SX, 396.0)
STAFF_RUN, STAFF_REACH = 80.0, 4.0

ORB_X, ORB_R = 238.0, 36.0
ORB_C = (ORB_X, 462.0)
ORB_GRIP = (ORB_X, 388.0)                      # the king's right hand holds the cone's stalk
ORB_STALK_TOP = 374.0
ORB_RUN, ORB_REACH = 80.0, 4.0

FACE = dict(lids="heavy", lid_sag=3.6, pupil_tuck=-1.8, brow_drop=4.0, brow_sag=2.8, brow_out=37.0, nose_bot_dy=23.0)
COLLAR = dict(link_w=18.0, bead_r=8.4, link_len=30.0, centre_gap=13.0)
HAIR = dict(top=(-54.0, -30.0), bulge=(-66.0, 40.0), bottom=(-55.0, 110.0), ribbons=4)
BEARD = dict(n=2, pitch=15.0, tick=6.0, tick_angle=40.0)
CROWN = dict(H=64.0, widths=(34.0, 38.0, 44.0, 38.0, 34.0), xs=(-60.0, -31.0, 0.0, 31.0, 60.0), knob=0.24,
             side_k=1.8, order="front", flute_mode="half", half_joint=False, centre_mode="one", hatch_phase=(2.0, 3.0), band_hw=78.0,
             wave_top=(26.0, 2.6), ripple=(2, 26.0, 2.2))
BIRD = dict(wing=((10.0, -46.0), (-2.0, -39.0), (-5.0, -25.0), (0.0, -10.0), (22.0, 9.0), (22.5, -14.0),
                  (19.5, -34.0), (15.0, -45.0)),
            tail=((9.0, -8.0), (20.0, -14.0), (30.0, 10.0), (20.0, 15.0)), collar=(-62.0, -51.0), belt_y=(-47.5, -37.0),
            vent=((-2.0, -6.0), (12.0, -12.0), (24.0, 8.0), (14.0, 8.0), (6.0, 3.0)))
ORB = dict(rings=RG.CONE_WHORLS, jitter=5.0, spin=0.0, tilt=-38.0, roll=0.0, crinkle=1.2, bulge=3.0, umbo_d=3.4,
           wrinkles=3, hatch_side=1, term_lon=25.0, stem=None)


def sleeve_end(hand, *, run, reach=0.0, cuff=3.0, flare=14.0, curl=-5.0, elbow_r=9.0):
    """The robe's own sleeve: a bell that opens from the cuff mouth toward the elbow, running to the
    robe's outer edge so the garment outline is the sleeve's far end."""
    u = hand.wrist_dir
    w = K.P(hand.wrist) - u * reach
    n = np.array([u[1], -u[0]])
    half = hand.wrist_w / 2
    base = w + u * run
    shape = K.R(K.Path(w + n * (half + cuff)).sag(w - n * (half + cuff), curl)
                .sag(base - n * (half + cuff + flare), 1.5).line(base + n * (half + cuff + flare))
                .sag(w + n * (half + cuff), 1.5).close().d)
    shape = shape.buffer(-1.6).buffer(1.6)
    elbow = shape.buffer(-elbow_r).buffer(elbow_r)
    mouth = shape.intersection(Polygon([w - n * 60 - u * 4, w + n * 60 - u * 4,
                                        w + n * 60 + u * 16, w - n * 60 + u * 16]))
    return K.U(elbow, mouth).intersection(KG.barrel().buffer(1.0))


def cuff_band(hand, sleeve, *, reach, offset=9.0, curl=-5.0, cuff=3.0):
    """A turn-back line parallel to the cuff mouth, inside the sleeve."""
    u = hand.wrist_dir
    n = np.array([u[1], -u[0]])
    mouth = K.P(hand.wrist) - u * reach + u * offset
    half = hand.wrist_w / 2 + cuff + 8.0
    path = K.Path(mouth + n * half).sag(mouth - n * half, curl)
    pts = np.asarray(K.C.sample_d(path.d, 0.3)[0][0])
    edge = LineString(pts).intersection(sleeve.buffer(-0.3))
    out = K.C.Frag()
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 8.0:
            out += K.line(K.C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def sleeve_edges(sleeve, keep):
    """The sleeve's long folds: its edges inside the robe (the robe outline carries the rest)."""
    out = K.C.Frag()
    edge = K.R(sleeve).boundary.intersection(keep)
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 6.0:
            out += K.line(K.C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def sleeve_grain(hand, sleeve, *, inset=9.0):
    """Hatch along the forearm axis, so the sleeve grain differs from the robe's."""
    u = hand.wrist_dir
    ang = float(np.degrees(np.arctan2(u[1], u[0])))
    return K.hatch_in(sleeve.buffer(-inset), angle=ang, origin=tuple(hand.wrist))


def sleeved_hand(hand, sleeve):
    """The hand beyond its cuff mouth; the sleeve's edge is the hand's contour."""
    region = K._biggest(hand.shape.difference(sleeve))
    inner = hand.hand.meta.get("inner", K.C.Frag())
    return K.Part(region, K.C.Frag(), K.outline(region) + K.clip_in(inner, region.buffer(-5.0)),
                  {**hand.hand.meta, "hand_region": region})


def held_attribute(attribute, hand_cuff):
    """One outline at the hand and the held object, without a halo."""
    shape = K.U(attribute.shape, hand_cuff.shape).buffer(1.6).buffer(-1.6).simplify(0.2)
    fills = K.clip_in(attribute.fills, attribute.shape.difference(
        hand_cuff.shape.buffer(-K.MEDIUM / 2))) + hand_cuff.fills
    return K.Part(
        shape, fills,
        K.clip_out(attribute.lines.select(lambda m: m.role != "outline"), hand_cuff.shape, eps=0.2, trap=0.0)
        + hand_cuff.lines.select(lambda m: m.role != "outline")
        + K.clip_in(K.outline(hand_cuff.shape, role="grip-edge"), attribute.shape.buffer(2.0))
        + K.outline(shape, role="contour"), hand_cuff.meta)


def staff_part():
    """The fluted gold cypress staff: bead collars at the top (it seats the finial), the middle and the
    foot, a ferrule below."""
    st = RG.gold_staff(x=SX, top=STAFF_TOP, bottom=STAFF_BOTTOM, hw=12.0, collars=(STAFF_TOP, 300.0, STAFF_BOTTOM),
                       collar_hw=16.0, flute_dx=3.45, visible_to=2000.0)
    foot = K.R(K.Path((SX - 11.0, STAFF_BOTTOM)).line((SX + 11.0, STAFF_BOTTOM)).line((SX + 4.5, STAFF_BOTTOM + 26.0))
               .line((SX - 4.5, STAFF_BOTTOM + 26.0)).close().d).buffer(-1.5).buffer(1.5)
    collar = K.R(K.rrect(SX - 16.0, STAFF_BOTTOM - 3.7, SX + 16.0, STAFF_BOTTOM + 3.7, 3.2))
    shape = K.U(st.shape, foot)
    lines = K.clip_in(st.lines, shape.buffer(1.0)) + K.clip_out(K.outline(foot), collar, eps=-0.5, trap=0.0)
    return K.Part(shape, K.fill(shape, K.GOLD), lines, st.meta)


def orb_part():
    """The cypress cone hung from a short gilt stalk (its top end held inside the fist, a collar where it leaves the
    cone), so the hand wraps a stalk instead of cupping a sphere."""
    cone = RG.cone_orb6(ORB_C, ORB_R, **ORB)
    x = ORB_X
    top = ORB_C[1] - ORB_R
    rod = K.box(x - 5.0, ORB_STALK_TOP, x + 5.0, top + 12.0)
    c2 = K.R(K.rrect(x - 9.5, top - 3.7 - 2.0, x + 9.5, top + 3.7 - 2.0, 3.2))
    shape = K.U(cone.shape, rod, c2)
    lines = cone.lines + K.clip_out(K.outline(rod), K.U(cone.shape, c2), eps=-0.5, trap=0.0)
    lines += K.outline(c2)
    return K.Part(shape, K.fill(shape, K.GOLD), lines, cone.meta)


def figure(opts=None):
    sc = K.Scene()
    fc = K.face(HEAD, "frontal", age="elder", **FACE)
    size = K.hand_size(fc) * HAND_SCALE

    # king's LEFT (viewer's right): wrap on the staff, thumb up, forearm out and down into the robe's edge
    h_st = K.hand5(GRIP, -90.0, "wrap", size=size, hand="L", view="back", grip_w=24.0)
    sl_st = sleeve_end(h_st, run=STAFF_RUN, reach=STAFF_REACH, flare=10.0)
    cuff_st = sleeved_hand(h_st, sl_st)
    held_st = held_attribute(staff_part(), cuff_st)

    # king's RIGHT (viewer's left): wrap on the cone's stalk, thumb up, forearm out and down into the edge
    h_orb = K.hand5(ORB_GRIP, -90.0, "wrap", size=size, hand="R", view="back", grip_w=10.0)
    sl_orb = sleeve_end(h_orb, run=ORB_RUN, reach=ORB_REACH, flare=10.0)
    cuff_orb = sleeved_hand(h_orb, sl_orb)
    held_orb = held_attribute(orb_part(), cuff_orb)

    # ---- head ------------------------------------------------------------------------------
    hs = K.HairSpec(**HAIR)
    hair = [HR.hair_fall_clear(fc, side, hs, keep=1) for side in (-1, 1)]
    mo = K.moustache(fc, K.MoustacheSpec(root=(-1.5, 8.5), tip=(-32.0, 30.0), arch=7.0))
    beard = KB.spray_lines_beard(fc, mo, **BEARD)
    crown = CR.knee_crown(**CROWN)
    clasp = K.lion_clasp((AX, 372.0), 40.0)
    collar = KP.spray_collar(within=KG.barrel(), **COLLAR)
    finial = BD.kingfisher3((SX, 176.0), **BIRD)

    sleeves = K.U(sl_st, sl_orb)
    keep = KG.barrel().buffer(-0.4)
    robes = KG.garments(K.U(held_st.shape, held_orb.shape, finial.shape, collar.shape, clasp.shape,
                            *[p.shape for p in hair], beard.shape, crown.shape),
                        near=K.U(held_st.shape, held_orb.shape),
                        sleeves=sleeves,
                        cuff_bands=cuff_band(h_st, sl_st, reach=STAFF_REACH) + cuff_band(h_orb, sl_orb, reach=ORB_REACH),
                        sleeve_grain=sleeve_grain(h_st, sl_st) + sleeve_grain(h_orb, sl_orb),
                        sleeve_edges=sleeve_edges(sl_st, keep) + sleeve_edges(sl_orb, keep),
                        seam=LineString(F.seam_spec(SEAM)["points"]))

    sc.part("robes", robes)
    sc.part("collar", collar)
    sc.part("staff+hand+sleeve", held_st)
    sc.part("finial", finial)
    sc.part("orb+hand+sleeve", held_orb)
    for s, p in zip((-1, 1), hair):
        sc.part(f"hair{s}", p)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("beard", beard)
    sc.part("moustache", mo)
    sc.part("crown", crown)
    sc.part("clasp", clasp)
    return sc


def build():
    return figure().layers()
