"""art/KD.py — K♦ · The Warden of the Ford (creative brief §H.10): continuous double-head, two sleeve hands.

Strict profile left, the Dome Crown, the Key of the Ford upright in the axe position. The whole-card
textiles (art/_kd_garments.py) are C2 about the card centre: the jade open mantle (chain border and
ford-stone brocade), the red tabard in its opening (ashlar courses knocked out to paper) and the
Warden's sash, one jade baldric with gold rowels that runs from one king's shoulder through the
centre to the other's. The seam (SEAM, a gentle diagonal through the robes) is only the place where
the 180° copy takes over: no band, medallion or divider.

Hands (both ``K.hand5``, back view, posed by parameters):
  * the king's LEFT hand (viewer's right) wraps the key's stem under its bit, thumb up the shaft;
  * the king's RIGHT hand (viewer's left) lies on the sash, fingers across the band, thumb on the
    upper edge.
Each wrist continues a short jade sleeve that opens from the mantle's outer edge and ends in a gold
tooled-scroll cuff beside the hand.
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck import frames as F
from art import _kd_body as B
from art import _kd_crown as CR
from art import _kd_head as H
from art import _kd_garments as KG

DOUBLE_HEAD = "continuous"
SEAM = -8.0
AX = K.AX
HEAD = (388.0, 211.0)
HAND_SCALE = 0.82

KEY_X = 524.0
GRIP = (KEY_X, 372.0)
KEY_RUN, KEY_REACH = 80.0, 4.0

REST_AT, REST_ANGLE = (204.0, 398.0), -22.0     # the sash hand's wrist and its wrist-to-fingertip direction
REST_RUN, REST_REACH = 80.0, 4.0
CLASP_S = -112.0                                 # the Lion Mark: offset along the sash from the card centre

SPRIG = dict(r0=7.8, q=5.6, flat=2.8, leaf=(11.5, 5.0), x_first=4.5, yc=3.0, free=True)


def sleeve_end(hand, *, run, reach=0.0, cuff=3.0, flare=14.0, curl=-5.0, elbow_r=9.0):
    """The mantle's own sleeve: a bell that opens from the cuff mouth toward the elbow, running to the
    mantle's outer edge so the garment outline is the sleeve's far end."""
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
    return K.U(elbow, mouth).intersection(KG.barrel())


def cuff_zone(hand, sleeve, *, reach, depth, curl=-5.0, cuff=3.0):
    """The gold cuff: the sleeve's last ``depth`` px beside the hand, its back edge a shallow arc."""
    u = hand.wrist_dir
    n = np.array([u[1], -u[0]])
    mouth = K.P(hand.wrist) - u * reach + u * depth
    half = hand.wrist_w / 2 + cuff + 14.0
    path = K.Path(mouth + n * half).sag(mouth - n * half, curl)
    pts = np.asarray(K.C.sample_d(path.d, 0.3)[0][0])
    w = K.P(hand.wrist) - u * reach
    back = Polygon(np.vstack([[w + n * (half + 6) - u * 6], [w - n * (half + 6) - u * 6], pts[::-1]]))
    return sleeve.intersection(back.buffer(0)), pts


def cuff_line(sleeve, pts):
    edge = LineString(pts).intersection(sleeve.buffer(-0.3))
    out = K.C.Frag()
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 8.0:
            out += K.line(K.C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def cuff_sprig(hand, sleeve, zone, *, reach, depth, mirror=False):
    """ONE unit of §G.31 tooled scroll across the gold cuff, kept clear of its edges."""
    u = hand.wrist_dir
    w = K.P(hand.wrist) - u * reach
    width = hand.wrist_w + 6.0
    g = B.gauntlet(w + u * depth, u, width=width, flare=width + 2.0, depth=depth, sprig=SPRIG, mirror=mirror)
    keep = zone.buffer(-(K.MEDIUM / 2 + 4.2))
    return K.clip_in(g.lines.select(lambda m: m.role != "outline"), keep)


def sleeve_edges(sleeve, keep):
    """The sleeve's long folds: its edges inside the mantle (the mantle outline carries the rest)."""
    out = K.C.Frag()
    edge = K.R(sleeve).boundary.intersection(keep)
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 6.0:
            out += K.line(K.C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def sleeve_grain(hand, sleeve, *, inset=9.0, skip=None):
    """Hatch along the forearm axis, so the sleeve grain differs from the mantle's."""
    u = hand.wrist_dir
    ang = float(np.degrees(np.arctan2(u[1], u[0])))
    reg = sleeve.buffer(-inset)
    if skip is not None:
        reg = reg.difference(skip)
    return K.hatch_in(reg, angle=ang, origin=tuple(hand.wrist))


def sleeved_hand(hand, sleeve):
    """The hand beyond its cuff mouth; the sleeve's edge is the hand's contour."""
    region = K._biggest(hand.shape.difference(sleeve))
    inner = hand.hand.meta.get("inner", K.C.Frag())
    return K.Part(region, K.C.Frag(), K.outline(region) + K.clip_in(inner, region.buffer(-5.0)),
                  {**hand.hand.meta, "hand_region": region})


def held_attribute(attribute, hand_cuff):
    """One outline at the hand and the held object, without a halo."""
    shape = K.U(attribute.shape, hand_cuff.shape).buffer(1.6).buffer(-1.6).simplify(0.02)
    fills = K.clip_in(attribute.fills, attribute.shape.difference(
        hand_cuff.shape.buffer(-K.MEDIUM / 2))) + hand_cuff.fills
    return K.Part(
        shape, fills,
        K.clip_out(attribute.lines.select(lambda m: m.role != "outline"), hand_cuff.shape, eps=0.2, trap=0.0)
        + hand_cuff.lines.select(lambda m: m.role != "outline")
        + K.clip_in(K.outline(hand_cuff.shape, role="grip-edge"), attribute.shape.buffer(2.0))
        + K.outline(shape, role="contour"), hand_cuff.meta)


def key_part():
    return B.key_of_ford(KEY_X, bow_c=(KEY_X, 124.0), ring_r=(40.0, 30.0), star_r=22.2, star_w=10.5, core_r=7.5,
                         stem_hw=11.0, collar_hw=15.5, collars=(174.0, 250.0, 326.0), bit_out=(38.0, 25.0),
                         stones=(212.0, 288.0), ward=(454.0, 6.8, 14.0))


def figure():
    sc = K.Scene()
    fc = H.profile_face(HEAD)
    g = H.gold_mass(fc, H.MassSpec(top_y=174.0, hair_foot=299.0, beard_foot=324.0))
    size = K.hand_size(fc) * HAND_SCALE
    seam = LineString(F.seam_spec(SEAM)["points"])

    # king's LEFT (viewer's right): wrap on the key's stem, thumb up, forearm out and down into the mantle's edge
    h_key = K.hand5(GRIP, -90.0, "wrap", size=size, hand="L", view="back", grip_w=22.0)
    sl_key = sleeve_end(h_key, run=KEY_RUN, reach=KEY_REACH, flare=10.0)
    cuff_key = sleeved_hand(h_key, sl_key)
    held_key = held_attribute(key_part(), cuff_key)

    # king's RIGHT (viewer's left): lies on the sash, thumb on the upper edge, forearm out and down into the edge
    h_rest = K.hand5(REST_AT, REST_ANGLE, "rest", size=size, hand="R", view="back", curl=25.0)
    sl_rest = sleeve_end(h_rest, run=90.0, reach=REST_REACH, flare=10.0)
    cuff_rest = sleeved_hand(h_rest, sl_rest)

    # ---- head ------------------------------------------------------------------------------
    skin = fc.skin.intersection(K.box(0.0, 0.0, 750.0, 299.0))
    hair = H.hair(fc, g, n=4)
    beard = H.beard(fc, g)
    mo = H.profile_moustache(fc)
    crown = CR.dome_crown(CR.DomeSpec(ax=394.0, base=186.0, circlet_h=15.0, drum_h=21.0, cornice_h=6.5,
                                      dome_h=40.0, lantern_h=9.0, cap_r=9.5, finial_d=11.5,
                                      rib_span=30.0, stone=(10.0, 4.8), stone_span=32.0, stone_dy=0.3,
                                      hatch_shift=3.5))
    c, u, n = KG.sash_axis()
    clasp_c = tuple(c + u * CLASP_S)
    clasp = K.lion_clasp(clasp_c, 40.0)

    # ---- garments ----------------------------------------------------------------------------
    sleeves = K.U(sl_key, sl_rest)
    keep = KG.barrel().buffer(-0.4)
    cz_key, pts_key = cuff_zone(h_key, sl_key, reach=KEY_REACH, depth=26.0)
    cz_rest, pts_rest = cuff_zone(h_rest, sl_rest, reach=REST_REACH, depth=26.0)
    cuff_fills = K.fill(cz_key, K.GOLD) + K.fill(cz_rest, K.GOLD)
    cuff_lines = (cuff_line(sl_key, pts_key) + cuff_line(sl_rest, pts_rest)
                  + cuff_sprig(h_key, sl_key, cz_key, reach=KEY_REACH, depth=26.0)
                  + cuff_sprig(h_rest, sl_rest, cz_rest, reach=REST_REACH, depth=26.0, mirror=True))
    front = K.U(held_key.shape, cuff_rest.shape, skin, hair.shape, beard.shape, mo.shape, crown.shape,
                clasp.shape)
    sash = KG.sash(clasp=clasp_c, avoid=K.U(front, sl_rest, sl_key), seam=seam)
    robes = KG.garments(K.U(front, sash.shape.buffer(0.0)),
                        sleeves=sleeves, cuff_fills=cuff_fills, cuff_lines=cuff_lines,
                        sleeve_grain=sleeve_grain(h_key, sl_key, skip=cz_key.buffer(4.0))
                        + sleeve_grain(h_rest, sl_rest, skip=cz_rest.buffer(4.0)),
                        sleeve_edges=sleeve_edges(sl_key, keep) + sleeve_edges(sl_rest, keep), seam=seam)

    sc.part("robes", robes)
    sc.part("sash", sash)
    sc.part("key+hand+sleeve", held_key)
    sc.part("hand", cuff_rest)
    sc.add("head", fc.lines + K.outline(skin), skin)
    sc.add("ear", H.ear_marks(g), None)
    sc.part("hair", hair)
    sc.part("beard", beard)
    sc.part("moustache", mo)
    sc.part("crown", crown)
    sc.part("clasp", clasp)
    return sc


def build():
    return figure().layers()
