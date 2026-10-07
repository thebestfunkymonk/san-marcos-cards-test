"""art/JD.py — J♦ · The Herald of the Road (House of the Ford), creative brief §H.12: continuous double-head,
two sleeve hands.

The court's messenger on El Camino Real, announcing arrivals at the crossing. 3/4 RIGHT; lips closed, gaze along
the trumpet. The whole-card textiles (art/_jd_garments.py) are C2 about the card centre: the jade mantle with its
ford-stone brocade and the red tabard column (stepping-stone chain knocked out round its edge, gold rowels in a
half-drop grid). The seam (SEAM, a gentle diagonal through the robes) is only the place where the 180° copy takes
over: no band, medallion or divider.

Hands (both ``K.hand5``, back view, posed by parameters):
  * the herald's LEFT hand (viewer's right) wraps the herald's trumpet below the banner, thumb up the tube;
  * the herald's RIGHT hand (viewer's left) wraps the thick rolled end of the map scroll, thumb up the roll.
Each wrist continues a short jade sleeve that opens from the mantle's outer edge and ends in a gold pearled
cuff beside the hand.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deck import courtkit as K  # noqa: E402
from deck import frames as F  # noqa: E402
from art import _jd_garments as KG  # noqa: E402
from art import _jd_parts as J  # noqa: E402

DOUBLE_HEAD = "continuous"
SEAM = -8.0
P = K.P
HEAD = (382.0, 207.0)
HAND_SCALE = 0.82

AXIS = -76.0                       # the trumpet's axis (toward the bell)
GRIP_A, S_GRIP = (510.0, 392.0), 267.0
TUBE_W = 18.0
LASH = 84.0                        # the banner rod lashes to the tube here (s from the mouth)
BANNER = (64.0, 38.0, 80.0)        # left and right of the rod's crossing, drop from the rod
A_RUN, A_REACH = 80.0, 4.0

GRIP_B = (262.0, 455.0)            # the map's thick left roll
MAP = (262.0, 362.0, 426.0, 484.0)
ROLL_W = 25.0
B_RUN, B_REACH = 88.0, 4.0

BELT = (441.0, 473.0)              # the belt's top and bottom
BUCKLE = (396.0, 456.0)
BELT_SCROLL = dict(x_first=427.5, n=1, tail=0.6, r0=8.6, q=8.4, flat=2.5, leaf=(17.2, 6.4), pet=0.9, dy=0.3,
                   lead_x=400.0)
CUFF_DEPTH = 26.0
NEAR_LIFT = 0.35                   # the near pupil raised clear of the lower lid (see ``pupils``)


def pupils(fc):
    """The far eye of the 3/4 face is 70 % wide and only ≈ 3.8 px open under raised lids: a Ø6 pupil hung
    from its lid either vanishes under it or grazes the lower lid (a hairline wedge). Seat it in the middle of
    the opening instead, across both lids (≈ 1 px into each): a dark iris in a narrow, turned-away eye. The
    near pupil keeps the kit's placement, lifted ``NEAR_LIFT`` px: the kit sets it 3.0 px off the lower lid at
    its centre line, but the lid's curve comes to 2.9 px at its lower right, and the heal then shaved it into
    a notched polygon."""
    ax, ey = fc.anchors["axis"], fc.anchors["eye_y"]
    keep, far, near = [], None, None
    for m in fc.lines.marks:
        if m.role == "pupil":
            if float(m.d[1:].split()[0]) + 3.0 > ax:
                far = m
            else:
                near = m
        else:
            keep.append(m)
    f = K.C.Frag(keep)
    if near is not None:
        x, y = (float(v) for v in near.d[1:].split("a")[0].split())
        f += K.dot((x + 3.0, y - NEAR_LIFT), 6.0, role="pupil")
    if far is not None:
        f += K.dot((float(far.d[1:].split()[0]) + 3.0, ey + 0.1), 6.0, role="pupil")
    fc.lines = f
    return fc


# ---------------------------------------------------------------------------
# sleeves
# ---------------------------------------------------------------------------
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


def cuff_pearls(hand, zone, *, reach, depth, pitch=9.0):
    """A row of ink pearls across the gold cuff, at mid-depth, kept clear of its edges."""
    u = hand.wrist_dir
    n = np.array([u[1], -u[0]])
    c = K.P(hand.wrist) - u * reach + u * depth * 0.5
    keep = zone.buffer(-(K.MEDIUM / 2 + 4.0))
    out = K.C.Frag()
    for k in (-1, 0, 1):
        p = c + n * pitch * k
        if keep.contains(shapely.Point(*p)):
            out += K.dot(p, 4.6, role="cuffline")
    return out


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
    shape = K.U(attribute.shape, hand_cuff.shape).buffer(1.6).buffer(-1.6).simplify(0.2)
    fills = K.clip_in(attribute.fills, attribute.shape.difference(
        hand_cuff.shape.buffer(-K.MEDIUM / 2))) + hand_cuff.fills
    return K.Part(
        shape, fills,
        K.clip_out(attribute.lines.select(lambda m: m.role != "outline"), hand_cuff.shape, eps=0.2, trap=0.0)
        + hand_cuff.lines.select(lambda m: m.role != "outline")
        + K.clip_in(K.outline(hand_cuff.shape, role="grip-edge"), attribute.shape.buffer(2.0))
        + K.outline(shape, role="contour"), hand_cuff.meta)


def figure():
    sc = K.Scene()
    # raised lids (the herald looks up along the trumpet) with the pupils showing below the RULE lid
    fc = K.face(HEAD, "3/4-right", age="young", lids="raised", pupil_dx=3.0, pupil_tuck=0.0)
    pupils(fc)
    size = K.hand_size(fc) * HAND_SCALE
    seam = LineString(F.seam_spec(SEAM)["points"])
    mouth = P(GRIP_A) + K.unit(AXIS) * S_GRIP
    T = J.Trumpet(mouth, AXIS)

    # herald's LEFT (viewer's right): wrap on the trumpet's tube, thumb up toward the bell, forearm out and down
    h_a = K.hand5(GRIP_A, AXIS, "wrap", size=size, hand="L", view="back", grip_w=TUBE_W)
    sl_a = sleeve_end(h_a, run=A_RUN, reach=A_REACH, flare=10.0)
    cuff_a = sleeved_hand(h_a, sl_a)
    tr = J.trumpet(T, tube_w=TUBE_W, mouth_hw=22.5, bell_len=48.0, lip=6.0, flare=2.8, knop=(48.0, 8.0),
                   boss=(190.0, 12.0), ferrules=(), ferrule=(6.0, 3.2), length=S_GRIP + 40.0,
                   mp=(8.0, 7.0, 7.0), hatch_bell="split", throat_merge=True)
    held_a = held_attribute(tr, cuff_a)

    rod_x, rod_y = (float(v) for v in T.at(LASH))
    bl, br_, bh = BANNER
    bx0, bx1, by1 = rod_x - bl, rod_x + br_, rod_y + bh
    tube_x = float(T.point_at_y(by1)[0][0]) + 9.0 / abs(T.u[1]) + K.MEDIUM / 2 + 3.2 + K.TD / 2
    bn = J.banner(bx0, rod_y, bx1, by1, seam=9.0, fringe=(10.5, 9.5, 13.0), avoid=tr.shape, fringe_x0=tube_x)

    # herald's RIGHT (viewer's left): wrap on the map's thick left roll, thumb up, forearm out and down
    h_b = K.hand5(GRIP_B, -90.0, "wrap", size=size, hand="R", view="back", grip_w=ROLL_W)
    sl_b = sleeve_end(h_b, run=B_RUN, reach=B_REACH, flare=10.0)
    cuff_b = sleeved_hand(h_b, sl_b)
    mp = J.map_open(*MAP, roll_l=ROLL_W, over_l=7.0, cap_l=7.0, crossing="gap",
                    river=(3, 7.8, 2.8, 4.6), route_pitch=7.4, gap=5.0)
    held_b = held_attribute(mp, cuff_b)

    # ---- belt and buckle on the tabard ----------------------------------------------------
    tab_all = KG.tabard_shape()
    buckle = J.lozenge_buckle(BUCKLE, L=36.0, W=38.0, inner=(14.0, 16.0))
    belt_box = K.box(250.0, BELT[0], 520.0, BELT[1]).intersection(tab_all.buffer(-0.5))
    over = K.U(buckle.shape, held_b.shape, held_a.shape)
    belt = J.tooled_belt(250.0, 520.0, BELT[0], BELT[1], tab_all.buffer(1.5), color=K.GOLD,
                         scroll=dict(BELT_SCROLL,
                                     keep=belt_box.difference(over.buffer(K.MEDIUM / 2 + 3.2 + K.FINE / 2))))

    # ---- head ---------------------------------------------------------------------------------
    fl = J.feather([(350, 182), (310, 184), (272, 192), (240, 210), (216, 236), (204, 266)], w_max=22.0,
                   w_tip=17.0, tip=30.0, n_lines=1, side=+1)
    fu = J.feather([(350, 180), (322, 160), (298, 138), (280, 114), (268, 90), (262, 66)], w_max=22.0,
                   w_tip=17.0, tip=30.0, n_lines=1, side=-1)
    band, crown = J.flat_cap(((346, 186), (434, 182), -2.0), ((348, 166), (432, 162), -3.0),
                             ((316, 172), (458, 162), 22.0, 9.0), band_color=K.GOLD)
    hair_out = [(304, 196), (298, 224), (298, 260), (304, 288), (320, 307), (342, 315)]
    hair = J.hair_bob([(346, 186), (336, 188), (304, 196), (298, 224), (298, 260), (304, 288), (320, 307),
                       (342, 316), (364, 310), (374, 292), (372, 258), (362, 228), (352, 206)], hair_out,
                      n=3, side=+1, stagger=9.0, first=10.0, cut=K.U(fl.shape, band.shape),
                      visible=K.box(0, 0, 2000, 2000).difference(fc.skin.buffer(1.0)))
    hair_r = J.hair_bob([(410, 180), (432, 178), (441, 188), (445, 212), (444, 236), (437, 252), (427, 258),
                         (418, 250), (418, 220)], [(437, 184), (444, 210), (443, 236), (434, 254)], n=1,
                        side=-1, stagger=0.0, first=10.0, cut=band.shape,
                        visible=K.box(0, 0, 2000, 2000).difference(fc.skin.buffer(1.0)))
    brooch = J.lozenge_buckle((350.0, 180.0), L=30.0, W=22.0, inner=(16.0, 11.0))
    ear = J.ear((342.0, 227.0), r=9.5, a0=90.0, a1=270.0, inner=False)

    # ---- garments ---------------------------------------------------------------------------------
    sleeves = K.U(sl_a, sl_b)
    keep = KG.barrel().buffer(-0.4)
    cz_a, pts_a = cuff_zone(h_a, sl_a, reach=A_REACH, depth=CUFF_DEPTH)
    cz_b, pts_b = cuff_zone(h_b, sl_b, reach=B_REACH, depth=CUFF_DEPTH)
    cuff_fills = K.fill(cz_a, K.GOLD) + K.fill(cz_b, K.GOLD)
    cuff_lines = (cuff_line(sl_a, pts_a) + cuff_line(sl_b, pts_b)
                  + cuff_pearls(h_a, cz_a, reach=A_REACH, depth=CUFF_DEPTH)
                  + cuff_pearls(h_b, cz_b, reach=B_REACH, depth=CUFF_DEPTH))
    col = K.R(K.Path((352.0, 282.0)).sag((420.0, 279.0), -4.0).line((428.0, 310.0)).sag((346.0, 303.0), 7.0)
              .close().d)
    skin = fc.skin
    front = K.U(held_a.shape, held_b.shape, belt.shape, buckle.shape, skin, hair.shape, hair_r.shape, crown.shape,
                band.shape, fl.shape, fu.shape, brooch.shape, bn.shape)
    robes = KG.garments(front, sleeves=sleeves, cuff_fills=cuff_fills, cuff_lines=cuff_lines,
                        sleeve_grain=sleeve_grain(h_a, sl_a, skip=cz_a.buffer(4.0))
                        + sleeve_grain(h_b, sl_b, skip=cz_b.buffer(4.0)),
                        sleeve_edges=sleeve_edges(sl_a, keep) + sleeve_edges(sl_b, keep), collar=col, seam=seam)

    sc.part("neck", K.neck(fc, bottom=312.0, width=36.0))
    sc.part("robes", robes)
    sc.part("belt", belt)
    sc.part("buckle", buckle)
    sc.part("hair", hair)
    sc.part("hairR", hair_r)
    sc.part("ear", ear)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("featherL", fl)
    sc.part("featherU", fu)
    sc.part("capband", band)
    sc.part("cap", crown)
    sc.part("brooch", brooch)
    sc.part("trumpet+hand+sleeve", held_a)
    sc.part("banner", bn)
    sc.add("fringe", bn.meta["fringe"], None, sil=False)
    sc.part("rod", J.rod((bx0 - 8.0, rod_y), (bx1 + 3.0, rod_y), h=9.5, finial=5.8))
    sc.part("lion", K.lion_clasp(tuple(bn.meta["centre"] + P(0, -3.4)), 60.0))
    sc.part("map+hand+sleeve", held_b)
    return sc


def build():
    return figure().layers()
