"""art/QD.py — Q♦ · The Queen of Scales (House of the Ford), creative brief §H.11: continuous double-head, two cloak-sleeve hands.

Justice of the square, after the figure on the courthouse dome: she weighs the kingdom's water, and this
Justice sees. 3/4 right, eyes open and level.

The whole-card textiles (art/_qd_garments.py) are C2 about the card centre: the Gill Red cape with its
stepping-stone chain and the jade arcade gown run from one queen's shoulders to the other's, so the seam
(SEAM, a gentle diagonal through the robes) is only the place where the 180° copy takes over: no band,
medallion or divider.

Hands (both ``K.hand5``, back view, posed by parameters):
  * the queen's LEFT hand (viewer's right) wraps the scales' staff below the lower collar, thumb up;
  * the queen's RIGHT hand (viewer's left) wraps the stem of a sprig of Texas paintbrush, thumb up the stem.
Each wrist continues a short red sleeve that opens from the cape's outer edge and ends in a gold cuff with
ink stones beside the hand.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck import frames as F
from deck.motifs import core as C
from art import _qd_parts as Q
from art import _qd_hair as H
from art import _qd_regalia as RG
from art import _qd_garments as QG
from art import _qd_finish as FIN

DOUBLE_HEAD = "continuous"
SEAM = 10.0
HEAD = (372.0, 206.0)
AXF = HEAD[0] + 0.12 * 84.0             # the face's feature axis (3/4 right: +12 % of the head width)
NECK_X = 380.0
HAND_SCALE = 0.82

COLLAR_SH_R = (-123.0, 320.0)           # far wing's shoulder point (the near wing's is (-134, 320))
JAW = (16.0, 49.0)                      # chin circle radius, its centre below the egg centre
STOM_TOP = 346.0
CLASP = (AXF + 1.0, 317.0)              # on the neckline: it runs into the wing tips as clean T-junctions
DIADEM_STONE = (9.0, 4.4)
DIADEM_KW = dict(cornice=False, stone_dy=1.0, foot_dy=-0.5, capitals=False)

STAFF_X = 529.0
BEAM_HALF = 47.0
STAFF_RINGS = (234.0, 284.0)
STAFF_HW = 9.0
STAFF_BOTTOM = 440.0
GRIP_S = (STAFF_X, 396.0)
CUFF_DEPTH = 28.0
SLEEVE_S = dict(run=84.0, reach=4.0, flare=10.0)

PB_AXIS = -96.6                         # the stem's up-axis (screen degrees); the thumb end
GRIP_B = (236.0, 410.0)
PB_STEM_BELOW, PB_LENGTH = 38.0, 252.0
STEM_W = 8.4
SLEEVE_B = dict(run=84.0, reach=4.0, flare=10.0)

PAINTBRUSH = dict(spike=100.0, top=(20.0, 11.0, 0.84), hatch_side=+1, root=4.0, stem_top=0.0, leaves_behind=True,
                  midribs=False,     # an 11 px leaf has no room for a FINE midrib (heal deleted them)
                  bracts=((0.00, +1, 46.0, 34.0, 17.0, 0.40), (0.09, -1, 38.0, 33.0, 17.0, 0.42),
                          (0.25, +1, 33.0, 30.0, 15.5, 0.48), (0.34, -1, 30.0, 29.0, 15.0, 0.52),
                          (0.49, +1, 24.0, 26.0, 13.5, 0.60), (0.57, -1, 21.0, 24.0, 12.5, 0.66),
                          (0.68, +1, 16.0, 22.0, 11.5, 0.74), (0.75, -1, 13.0, 20.0, 11.0, 0.80)),
                  leaves=((0.43, -1, 34.0, 11.0), (0.68, +1, 32.0, 10.5)))

# the hair, dressed up: swept back from the brow over the ear into a knot at
# the nape (the ear and a ♦ drop earring show; the neck is bare)
MANE_OUT = [(318.0, 164.0), (302.0, 184.0), (292.0, 210.0), (288.0, 240.0), (290.0, 270.0), (296.0, 300.0),
            (302.0, 330.0)]
MANE_IN = [(360.0, 166.0), (352.0, 200.0), (352.0, 240.0), (372.0, 274.0), (372.0, 330.0)]
FAR_OUT = [(424.0, 166.0), (431.0, 190.0), (433.0, 220.0), (431.0, 252.0), (434.0, 284.0), (440.0, 320.0)]
FAR_IN = [(396.0, 166.0), (404.0, 200.0), (400.0, 240.0), (388.0, 274.0), (388.0, 320.0)]
EAR = ((332.5, 214.0), (316.0, 226.0), (331.0, 245.0))
EAR_IN = ((329.0, 220.5), (322.5, 228.0), (328.0, 236.0))
EARRING = (331.0, 249.0)


def sleeve_end(hand, *, run, reach=0.0, cuff=3.0, flare=14.0, curl=-5.0, elbow_r=9.0):
    """The cape's own sleeve: a bell that opens from the cuff mouth toward the elbow, running to the
    cape's outer edge so the garment outline is the sleeve's far end."""
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
    return K.U(elbow, mouth).intersection(QG.cape_shape())


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


def cuff_stones(hand, zone, *, stone=(12.0, 6.0), pitch=8.8):
    """§G.23 ink stones across the cuff, long axis along the forearm, on the cuff's centroid and clear of its edges."""
    u = hand.wrist_dir
    n = np.array([u[1], -u[0]])
    mid = np.array(zone.centroid.coords[0])
    ang = math.degrees(math.atan2(u[1], u[0]))
    room = zone.buffer(-(K.MEDIUM / 2 + 3.2))
    out = C.Frag()
    for k in range(-5, 6):
        p = mid + n * (k * pitch)
        lz = K.R(C.lozenge_d(p[0], p[1], stone[0], stone[1], ang))
        if room.contains(lz):
            out += K.fill(lz, K.INK, role="stone")
    return out


def sleeve_edges(sleeve, keep):
    """The sleeve's long folds: its edges inside the cape (the cape outline carries the rest)."""
    out = K.C.Frag()
    edge = K.R(sleeve).boundary.intersection(keep)
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 6.0:
            out += K.line(K.C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def sleeve_grain(hand, sleeve, *, inset=9.0, skip=None):
    """Hatch along the forearm axis, so the sleeve grain differs from the cape's."""
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


def staff_part(bal):
    """The scales' staff: the balance's gold shaft ending in a ferrule above the seam."""
    st = bal["staff"]
    x, y = STAFF_X, STAFF_BOTTOM
    foot = K.R(K.Path((x - STAFF_HW, y)).line((x + STAFF_HW, y)).line((x + 4.0, y + 22.0))
               .line((x - 4.0, y + 22.0)).close().d).buffer(-1.0).buffer(1.0)
    shape = K.U(st.shape, foot)
    seat = K.U(foot, K.box(x - STAFF_HW, y - 6.0, x + STAFF_HW, y + 1.0))
    return K.Part(shape, st.fills + K.fill(seat, K.GOLD), st.lines + K.outline(foot), st.meta)


def paintbrush_part():
    u = np.array([math.cos(math.radians(PB_AXIS)), math.sin(math.radians(PB_AXIS))])
    base = K.P(GRIP_B) - u * PB_STEM_BELOW
    tip = base + u * PB_LENGTH
    return Q.paintbrush7(tuple(base), tuple(tip), stem_w=STEM_W, **PAINTBRUSH)


def figure():
    sc = K.Scene()
    fkw = dict(sex="f", age="adult", lids="heavy", flick=0.0, brow_dy=-15.0, brow_sag=4.4, mouth_hw=8.5,
               bow_rise=2.0, bow_sag=-0.6, lip_hw=4.8, lip_sag=-2.0, lip_dy=44.0, pupil_tuck=-0.5)
    fc = K.face(HEAD, "3/4-right", **fkw)
    # a queen's jaw: the kit egg with a smaller chin circle set a little lower
    hd, _info = K.egg(HEAD, 42.0, chin_dx=0.12 * 84.0 * 0.55, chin_r=JAW[0], chin_dy=JAW[1])
    fc.head, fc.skin = hd, K.R(hd)
    size = K.hand_size(fc) * HAND_SCALE
    seam = LineString(F.seam_spec(SEAM)["points"])

    # queen's LEFT (viewer's right): wrap on the staff below the lower collar, thumb up, forearm out and down
    h_s = K.hand5(GRIP_S, -90.0, "wrap", size=size, hand="L", view="back", grip_w=2 * STAFF_HW)
    sl_s = sleeve_end(h_s, **SLEEVE_S)
    cuff_s = sleeved_hand(h_s, sl_s)
    bal = RG.balance(STAFF_X, half=BEAM_HALF, collars=STAFF_RINGS, pan_hw=23.0, surf_ry=13.0, pan_depth=7.0,
                     foot=None, beam_h=(16.0, 11.0), boss_r=8.0, staff_hw=STAFF_HW, staff_bottom=STAFF_BOTTOM,
                     pivot=False, neck_hw=2.4, fin_marks=False)
    held_s = held_attribute(staff_part(bal), cuff_s)

    # queen's RIGHT (viewer's left): wrap on the paintbrush stem, thumb up the stem, forearm out and down
    pb = paintbrush_part()
    h_b = K.hand5(GRIP_B, PB_AXIS, "wrap", size=size, hand="R", view="back", grip_w=STEM_W)
    sl_b = sleeve_end(h_b, **SLEEVE_B)
    cuff_b = sleeved_hand(h_b, sl_b)
    held_b = held_attribute(pb, cuff_b)

    # ---- head ------------------------------------------------------------------------
    dfr, dcol = RG.portico3(AXF + 1.5, xl=314.0, xr=428.0, top_l=160.0, top_c=162.0, top_r=160.0,
                            band_h=16.0, stone=DIADEM_STONE, stone_pitch=15.0, col_h=30.0, col_w=8.4,
                            cap=(2.6, 2.2), base=(0.0, 0.0), arch_h=8.0, ped_rise=23.0, ped_hw=(58.0, 47.0), vy=260.0,
                            oculus_r=6.5, oculus_at=0.29, oculus_pane=K.RED, **DIADEM_KW)
    hair_far = H.mane(outer=FAR_OUT, inner=FAR_IN, n=1, band=dfr.meta["band"])
    hair = H.mane(outer=MANE_OUT, inner=MANE_IN, n=4, band=dfr.meta["band"])
    collar = Q.standing_collar2(NECK_X, top_y=226.0, half_w=108.0, neck_y=268.0, shoulder=(-134.0, 320.0),
                                shoulder_r=COLLAR_SH_R, top_sag=8.0, side_sag=-5.0, rim=9.0, depth=60.0,
                                color=K.JADE, rim_color=K.GOLD)
    neck = H.neck_chest(NECK_X, top=236.0, hw=14.5, base_y=284.0, shoulder=(346.0, 404.0), spring_y=298.0,
                        bottom=306.0)
    stom = RG.stomacher3(AXF + 1.0, top=STOM_TOP, hw_top=38.0, hw_mid=33.0, y_mid=440.0, y_point=488.0)
    clasp = K.lion_clasp(CLASP, 40.0)
    eo = K.P(fc.anchors["axis"] - fc.anchors["spec"].eye_dx - fc.anchors["spec"].eye_w / 2, fc.anchors["eye_y"])
    lash = K.seg(eo, eo + K.P(-3.2, 1.2), K.RULE, role="lid")
    ear = H.ear2(*EAR, face=fc.skin, inner=EAR_IN)
    earring = H.earring(EARRING, bead=6.3, drop=(15.0, 9.5))

    # ---- garments ----------------------------------------------------------------------------
    front = K.U(held_s.shape, held_b.shape, neck.shape, stom.shape, clasp.shape, fc.skin, dfr.shape, dcol.shape)
    sleeves = K.U(sl_s, sl_b)
    keep = QG.cape_shape().buffer(-0.4)
    cz_s, pts_s = cuff_zone(h_s, sl_s, reach=SLEEVE_S["reach"], depth=CUFF_DEPTH)
    cz_b, pts_b = cuff_zone(h_b, sl_b, reach=SLEEVE_B["reach"], depth=CUFF_DEPTH)
    cuff_fills = K.fill(cz_s, K.GOLD) + K.fill(cz_b, K.GOLD)
    cuff_lines = (cuff_line(sl_s, pts_s) + cuff_line(sl_b, pts_b)
                  + cuff_stones(h_s, cz_s) + cuff_stones(h_b, cz_b))
    cape = QG.cape(front, sleeves=sleeves, cuff_fills=cuff_fills, cuff_lines=cuff_lines,
                   sleeve_grain=sleeve_grain(h_s, sl_s, skip=cz_s.buffer(4.0))
                   + sleeve_grain(h_b, sl_b, skip=cz_b.buffer(4.0)),
                   sleeve_edges=sleeve_edges(sl_s, keep) + sleeve_edges(sl_b, keep), seam=seam)
    gown = QG.gown(K.U(stom.shape, clasp.shape, neck.shape), seam=seam)

    sc.part("collar", collar)
    sc.part("hair", hair_far + hair)
    sc.part("cape", cape)
    sc.part("neck", neck)
    sc.part("gown", gown)
    sc.part("stomacher", stom)
    sc.part("clasp", clasp)
    sc.add("head", fc.lines + lash + K.outline(fc.head), fc.skin)
    sc.part("ear", ear + earring)
    sc.part("diadem", dfr)
    sc.part("columns", dcol, sil=False)
    sc.part("staff+hand+sleeve", held_s)
    sc.part("beam", bal["beam"])
    sc.add("cords", bal["cords"].lines, None, sil=False)
    sc.part("panL", bal["panL"], sil=False)
    sc.part("panR", bal["panR"], sil=False)
    sc.part("paintbrush+hand+sleeve", held_b, sil=False)
    return sc


def build():
    return K.layers(FIN.compose(figure()))
