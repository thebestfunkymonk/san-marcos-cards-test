"""K♠ · The King Beneath (creative brief §H.1): continuous double-head, two cloak-sleeve hands.

Whole-card textiles (art/_ks_garments.py): the jade barrel mantle with a hatched border and
strata + the Balcones fault, the red lapels with rising bubbles, the karst-void lens tunic and
the two sleeves are C2 about the card centre, so the seam (SEAM, a gentle diagonal through the
robes) is only a place where the 180° copy takes over — no band, medallion or divider.

Hands (both ``K.hand5``, back view, posed by parameters):
  * the king's LEFT hand (viewer's right) wraps the core sceptre, thumb up the shaft;
  * the king's RIGHT hand (viewer's left) wraps the short stem of the spring-vent orb.
Each wrist continues a short jade sleeve that opens from the mantle's outer edge, so the
mantle outline is the sleeve's far end and its cuff mouth is the turn-back beside the hand.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck import frames as F
from art import _ks_garments as KG

DOUBLE_HEAD = "continuous"
SEAM = 10.9
AX = K.AX
HEAD = (AX, 207.0)
HAND_SCALE = 0.82

SX = 508.0                                     # sceptre axis
SC_TOP, SC_BOTTOM, FIN_C = 148.0, 452.0, (SX, 100.0)
GRIP = (SX, 396.0)
SC_RUN, SC_REACH = 80.0, 4.0

ORB_X, ORB_R = 236.0, 33.0
ORB_C = (ORB_X, 376.0)
ORB_GRIP = (ORB_X, 454.0)                      # the king's right hand wraps the orb's short stem
ORB_FOOT = 494.0
ORB_GAPS = (8.2, 10.6, 13.8)
ORB_RUN, ORB_REACH = 80.0, 4.0


def sleeve_end(hand, *, run, reach=0.0, cuff=3.0, flare=14.0, curl=-5.0, elbow_r=9.0):
    """The cloak's own sleeve: a bell that opens from the cuff mouth toward the elbow, running
    to the cloak's outer edge so the garment outline is the sleeve's far end."""
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
    """The sleeve's long folds: its edges inside the cloak (the cloak outline carries the rest)."""
    out = K.C.Frag()
    edge = K.R(sleeve).boundary.intersection(keep)
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 6.0:
            out += K.line(K.C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def sleeve_grain(hand, sleeve, *, inset=9.0):
    """Hatch along the forearm axis, so the sleeve grain differs from the mantle's."""
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
    shape = K.U(attribute.shape, hand_cuff.shape).buffer(1.6).buffer(-1.6).simplify(0.02)
    fills = K.clip_in(attribute.fills, attribute.shape.difference(
        hand_cuff.shape.buffer(-K.MEDIUM / 2))) + hand_cuff.fills
    return K.Part(
        shape, fills,
        K.clip_out(attribute.lines.select(lambda m: m.role != "outline"), hand_cuff.shape, eps=0.2, trap=0.0)
        + hand_cuff.lines.select(lambda m: m.role != "outline")
        + K.clip_in(K.outline(hand_cuff.shape, role="grip-edge"), attribute.shape.buffer(2.0))
        + K.outline(shape, role="contour"), hand_cuff.meta)


def sceptre_part():
    """The seven-segment core sceptre, with a collar and a ferrule at its foot."""
    spec = K.SceptreSpec(x=SX, hw=11.0, collar_hw=14.5, top=SC_TOP, bottom=SC_BOTTOM,
                         finial_c=FIN_C, visible_to=None)
    sp = K.sceptre(spec)
    collar = K.R(K.rrect(SX - 14.5, SC_BOTTOM - 3.7, SX + 14.5, SC_BOTTOM + 3.7, 3.2))
    foot = K.R(K.Path((SX - 10.0, SC_BOTTOM)).line((SX + 10.0, SC_BOTTOM)).line((SX + 4.0, SC_BOTTOM + 24.0))
               .line((SX - 4.0, SC_BOTTOM + 24.0)).close().d).buffer(-1.5).buffer(1.5)
    both = K.U(collar, foot)
    lines = K.clip_out(sp.lines, collar, eps=-0.5, trap=0.0) + K.outline(collar) \
        + K.clip_out(K.outline(foot), collar, eps=-0.5, trap=0.0)
    shape = K.U(sp.shape, both)
    return K.Part(shape, K.fill(shape, K.GOLD) + sp.fills.select(lambda m: m.color != K.GOLD), lines, sp.meta)


def orb_part():
    """The spring-vent orb on a short core stem (collar under the ball, ferrule at the foot), so
    the hand can wrap a stem instead of cupping a sphere. The vent bubble is its own item."""
    ball = K.R(K.circle(ORB_C, ORB_R))
    top = ORB_C[1] - ORB_R
    bc = K.P(ORB_C[0], top - K.MEDIUM - K.GAP - 13.0 / 2)
    x, yb = ORB_X, ORB_C[1] + ORB_R
    stem = K.box(x - 8.5, yb - 6.0, x + 8.5, ORB_FOOT)
    c1 = K.R(K.rrect(x - 12.5, yb - 3.7, x + 12.5, yb + 3.7, 3.2))
    c2 = K.R(K.rrect(x - 12.5, ORB_FOOT - 3.7, x + 12.5, ORB_FOOT + 3.7, 3.2))
    foot = K.R(K.Path((x - 9.0, ORB_FOOT)).line((x + 9.0, ORB_FOOT)).line((x + 3.5, ORB_FOOT + 20.0))
               .line((x - 3.5, ORB_FOOT + 20.0)).close().d).buffer(-1.5).buffer(1.5)
    shape = K.U(ball, stem, c1, c2, foot)
    lines = K.outline(ball)
    y = top + 5.5
    for g in ORB_GAPS:                         # ripples widen downward from the vent
        y += g
        dx = math.sqrt(max(ORB_R ** 2 - (y - ORB_C[1]) ** 2, 0.0))
        lines += K.line(K.arc_sag((ORB_C[0] - dx, y), (ORB_C[0] + dx, y), -(2.6 + 0.10 * (y - top))), K.FINE,
                        role="latitude")
    lines += K.clip_out(K.outline(stem), K.U(ball, c1, c2), eps=-0.5, trap=0.0)
    lines += K.outline(c1) + K.outline(c2) + K.clip_out(K.outline(foot), c2, eps=-0.5, trap=0.0)
    return K.Part(shape, K.fill(shape, K.GOLD), lines, {"c": K.P(ORB_C), "r": ORB_R}), bc


def figure():
    sc = K.Scene()
    fc = K.face(HEAD, "frontal", age="elder", lids="heavy")
    size = K.hand_size(fc) * HAND_SCALE

    # king's LEFT (viewer's right): wrap on the sceptre, thumb up, forearm out and down into the mantle's edge
    h_sc = K.hand5(GRIP, -90.0, "wrap", size=size, hand="L", view="back", grip_w=22.0)
    sl_sc = sleeve_end(h_sc, run=SC_RUN, reach=SC_REACH, flare=10.0)
    cuff_sc = sleeved_hand(h_sc, sl_sc)
    held_sc = held_attribute(sceptre_part(), cuff_sc)

    # king's RIGHT (viewer's left): wrap on the orb's stem, thumb up, forearm out and down into the edge
    h_orb = K.hand5(ORB_GRIP, -90.0, "wrap", size=size, hand="R", view="back", grip_w=17.0)
    sl_orb = sleeve_end(h_orb, run=ORB_RUN, reach=ORB_REACH, flare=10.0)
    cuff_orb = sleeved_hand(h_orb, sl_orb)
    orb, bc = orb_part()
    held_orb = held_attribute(orb, cuff_orb)
    bubble = K.Part(K.R(K.circle(bc, 6.5 + K.MEDIUM / 2)), K.C.Frag(), K.line(K.circle(bc, 6.5), K.MEDIUM, role="bubble"))

    # ---- head ------------------------------------------------------------------
    hs = K.HairSpec(bulge=(-65.0, 40.0), bottom=(-54.0, 108.0), ribbons=4)
    hair = [K.hair_fall(fc, side, hs) for side in (-1, 1)]
    mo = K.moustache(fc, K.MoustacheSpec(root=(-1.5, 8.5), tip=(-30.0, 25.0), arch=6.2))
    beard = K.beard(fc, K.BeardSpec(bulge=(-41.0, 72.0), tip=(-15.0, 124.0), notch_dy=95.0,
                                    stagger=13.0, lines=3), mo=mo)
    crown = K.merlon_crown()
    clasp = K.lion_clasp((AX, 358.0), 40.0)
    neckline = K.U(*[p.shape for p in hair], beard.shape, crown.shape)

    sleeves = K.U(sl_sc, sl_orb)
    keep = KG.barrel().buffer(-0.4)
    robes = KG.garments(K.U(held_sc.shape, held_orb.shape, bubble.shape, neckline, clasp.shape),
                        sleeves=sleeves,
                        cuff_bands=cuff_band(h_sc, sl_sc, reach=SC_REACH) + cuff_band(h_orb, sl_orb, reach=ORB_REACH),
                        sleeve_grain=sleeve_grain(h_sc, sl_sc) + sleeve_grain(h_orb, sl_orb),
                        sleeve_edges=sleeve_edges(sl_sc, keep) + sleeve_edges(sl_orb, keep),
                        seam=LineString(F.seam_spec(SEAM)["points"]))

    sc.part("collar", K.standing_collar(top_y=236.0, half_w=110.0, neck_y=262.0, shoulder=(-112.0, 312.0),
                                        side_sag=-3.0, rim=10.5))
    sc.part("robes", robes)
    sc.part("sceptre+hand+sleeve", held_sc)
    sc.part("orb+hand+sleeve", held_orb)
    sc.part("bubble", bubble, sil=False)
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
