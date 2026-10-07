"""art/QC.py — Q♣ · The Wild-Rice Queen (House of the Reed), creative brief §H.8: continuous double-head, two cloak-sleeve hands.

The whole-card textiles (art/_qc_garments.py) are C2 about the card centre: the red-lined cloak with its
jade turned-back edge, the jade leaf gown and the laced front run from one figure's shoulders to the
other's, so the seam (SEAM, a gentle diagonal through the robes) is only a place where the 180° copy
takes over: no band, medallion or divider.

Hands (both ``K.hand5``, back view, posed by parameters):
  * the queen's LEFT hand (viewer's right) wraps the wild-rice sceptre's culm below the lower node;
  * the queen's RIGHT hand (viewer's left) wraps the handle of the egret fan.
Each wrist continues a short jade sleeve that opens from the cloak's jade edge, so the cloak outline is
the sleeve's far end and its cuff mouth is the turn-back beside the hand.

Head, crown, hair, bertha, brooch, sceptre and plumes are the Q♣ parts of art/_qc_*.py:
    crown     gold   the rice-spike coronet (§H.8): a solid flared circlet with three wrought wild-rice sprays
    sceptre   gold   the flowering wild-rice stalk (§G.5): culm, knop, male florets hanging, female spikelets erect
    fan       paper  five egret plumes (§G.24) on a gold handle and ferrule
    brooch    gold   the Lion Mark, 40 px
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck import frames as F
from deck.motifs import core as C
from art import _qc_parts as Q
from art import _qc_sceptre as S
from art import _qc_fan as FN
from art import _qc_garments as QG

DOUBLE_HEAD = "continuous"
SEAM = -8.0
AX = K.AX
HEAD = (386.0, 206.0)
HAND_SCALE = 0.82

BERTHA = 35.0
PEARL = dict(d_end=6.3, d_mid=10.0, gap=6.5, margin=34.0)
BROOCH = (375.0, 336.0)

# ---- head -----------------------------------------------------------------------
HAIRLINE = ((343.0, 214.0), (371.0, 180.0), (428.0, 205.0))
HAIRLINE_ROUND = 14.0
HAIR_L = dict(outer=[(380, 157), (350, 158), (328, 169), (314, 192), (308, 218), (308, 242), (302, 268), (291, 294),
                     (283, 322), (278, 352)],
              inner=[(376, 157), (371, 180), (356, 193), (352, 212), (356, 235), (364, 252), (370, 266), (370, 284),
                     (364, 310), (354, 336), (346, 352)],
              n=3)
HAIR_R = dict(outer=[(380, 157), (414, 157), (442, 167), (462, 190), (472, 218), (473, 244), (480, 270), (492, 296),
                     (501, 325), (506, 352)],
              inner=[(385, 157), (393, 178), (410, 190), (418, 210), (418, 232), (410, 250), (400, 263), (397, 285),
                     (404, 312), (414, 352)],
              n=3)
FACE = dict(lids="level", pupil_dx=2.4, eye_dy=8.5, mouth_hw=9.5, bow_rise=1.8, bow_sag=-0.9, lip_hw=6.4, lip_sag=-2.6,
            mouth_dy=32.5, lip_dy=41.0, brow_dy=-16.5, brow_sag=5.0, nose_bot_dy=16.0)
FLICK = (5.0, -1.8)
NECK = ([(356, 236), (362, 262), (365, 285), (359, 312), (349, 336)],
        [(410, 236), (404, 262), (403, 285), (410, 312), (420, 336)])
CROWN = dict(cx=386.5, top=142.0, h=26.0, bow=4.0, hw=(58.0, 54.0), rim=8.5, base=8.0, jewel=(9.5, 144.5, 6.3),
             far=0.85, sink=5.0)
SPRAYS = ((-47.0, -2.0, 28.0, (21.0, 7.0, 14.0), ((8.0, -1, 12.0, 64.0, 19.0, 6.3, 12.0, 14.0),
                                                   (14.0, 1, 12.0, 66.0, 18.0, 6.0, 8.0, 13.0))),
          (51.0, 2.0, 28.0, (21.0, 7.0, 14.0), ((8.0, 1, 12.0, 64.0, 19.0, 6.3, 12.0, 14.0),
                                                 (14.0, -1, 12.0, 66.0, 18.0, 6.0, 8.0, 13.0))),
          (0.0, 0.0, 30.0, (23.0, 7.7, 15.0), ((13.0, -1, 12.0, 64.0, 20.0, 6.7, 10.0, 14.0),
                                               (19.0, 1, 13.0, 64.0, 20.0, 6.7, 10.0, 14.0))))

# ---- attributes -------------------------------------------------------------------
SCEPTRE_X = 524.0
SCEPTRE_HW = 9.5
GRIP_S = (SCEPTRE_X, 420.0)
SCEPTRE_BOTTOM = 486.0
SCEPTRE = dict(hw=SCEPTRE_HW, knop_y=286.0, knop_hw=13.0, knop_h=12.0, nodes=(344.0, 462.0), node_hw=13.0,
               node_h=9.0, striae=False, rachis_hw=3.0, rachis_top=132.0, terminal=(28.0, 8.4, 16.0),
               female=((206.0, -1, 13.0, 62.0, 27.0, 8.6, 13.0, 15.0), (190.0, 1, 13.0, 62.0, 27.0, 8.6, 13.0, 15.0),
                       (174.0, -1, 11.0, 60.0, 26.0, 8.4, 9.0, 15.0), (158.0, 1, 11.0, 60.0, 26.0, 8.4, 9.0, 15.0)),
               arms=((245.0, 66.0, ((12.0, 50.0), (19.0, 62.0), (6.0, 36.0)), 6.0,
                      ((0.33, 7.0, 22.0, 7.6, 0.0), (0.60, 7.0, 22.0, 7.6, 0.0)), None),),
               knop_ink=K.CONTOUR / 2)
SCEPTRE_RUN, SCEPTRE_REACH = 130.0, 8.0

GRIP_F = (246.0, 434.0)
FAN_AXIS = -90.0
FAN_HANDLE_W = 12.0
FAN_RUN, FAN_REACH = 130.0, 4.0
PLUMES = ((-150.0, 96.0, (-6.0, -36.0), 23.0), (-133.0, 118.0, (-8.0, -42.0), 25.0),
          (-117.0, 134.0, (-10.0, -46.0), 26.0), (-101.0, 146.0, (-12.0, -50.0), 26.0),
          (-85.0, 142.0, (-12.0, -52.0), 24.0))
FAN_KW = dict(split=0.42, w_root=8.0, peak=0.38, n=2, power=0.8, mode="vane", barb_room=1.5, barb=28.0,
              neck=50.0, root_dy=-6.0)


def sleeve_end(hand, *, run, reach=0.0, cuff=3.0, flare=14.0, curl=-5.0, elbow_r=9.0):
    """The cloak's own sleeve: a bell that opens from the cuff mouth toward the elbow, running to the
    cloak's outer edge so the garment outline is the sleeve's far end."""
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
    return K.U(elbow, mouth).intersection(QG.cloak_shape().buffer(-0.6))


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
    """The sleeve's long folds: its edges inside the cloak's lining (the jade edge carries the rest)."""
    out = K.C.Frag()
    edge = K.R(sleeve).boundary.intersection(keep)
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 6.0:
            out += K.line(K.C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def sleeve_grain(hand, sleeve, *, inset=9.0):
    """Hatch along the forearm axis, so the sleeve grain differs from the gown's."""
    u = hand.wrist_dir
    ang = float(np.degrees(np.arctan2(u[1], u[0])))
    return K.hatch_in(sleeve.buffer(-inset), angle=ang, origin=tuple(hand.wrist))


def sleeve_part(hand, sleeve, *, reach):
    keep = QG.cloak_shape().buffer(-QG.EDGE + 0.4)
    lines = sleeve_edges(sleeve, keep) + cuff_band(hand, sleeve, reach=reach) + sleeve_grain(hand, sleeve)
    return K.Part(sleeve, K.fill(sleeve, K.JADE), lines, {})


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
    """The wild-rice sceptre; its culm ends in a gold ferrule above the seam."""
    sp = S.rice_sceptre(SCEPTRE_X, bottom=SCEPTRE_BOTTOM, **SCEPTRE)
    x, y = SCEPTRE_X, SCEPTRE_BOTTOM
    foot = K.R(K.Path((x - SCEPTRE_HW, y)).line((x + SCEPTRE_HW, y)).line((x + 4.0, y + 24.0))
               .line((x - 4.0, y + 24.0)).close().d).buffer(-1.0).buffer(1.0)
    shape = K.U(sp.shape, foot)
    lines = sp.lines + K.outline(foot)
    return K.Part(shape, sp.fills + K.fill(foot, K.GOLD), lines, {**sp.meta, "culm": K.U(sp.meta["culm"], foot)})


def head_group(sc, fc):
    """head, hair under the crown, hair locks (in front of the head, clipped
    round the face and below the circlet's top edge), rice crown → the Face"""
    a = fc.anchors
    s = a["spec"]
    oc = K.P(float(a["axis"]) + s.eye_dx + s.eye_w / 2, a["eye_y"])
    flick = K.seg(oc, oc + K.P(*FLICK), K.RULE, role="lid")
    sc.add("head", fc.lines + flick + K.outline(fc.head), fc.skin)
    zone = K.R(fc.head).intersection(K.R(K.arc3(*HAIRLINE) + "L520 600L240 600Z").buffer(0))
    zone = zone.buffer(-HAIRLINE_ROUND, quad_segs=24).buffer(HAIRLINE_ROUND, quad_segs=24)
    cap = K.R(fc.head).difference(zone.buffer(0.01))
    cap = K._polys_of(cap.buffer(-1.0, quad_segs=12).buffer(1.0, quad_segs=12))
    cap = max(cap, key=lambda g: g.area)
    sc.part("hairC", K.Part(cap, K.fill(cap, K.GOLD), K.outline(cap), {}))
    cw = CROWN
    xl, xr = cw["cx"] - cw["hw"][0], cw["cx"] + cw["hw"][0]
    above = K.R(K.Path((200.0, -100.0)).line((xl, -100.0)).line((xl, cw["top"] - cw["bow"])).arc3(
        (cw["cx"], cw["top"]), (xr, cw["top"] - cw["bow"])).line((xr, -100.0)).line((600.0, -100.0)).line(
        (600.0, -150.0)).line((200.0, -150.0)).close().d)
    for nm, spec in (("hairL", HAIR_L), ("hairR", HAIR_R)):
        sc.part(nm, Q.hair_lock(fc, spec["outer"], spec["inner"], n=spec["n"], hairline=K.U(zone, above)))
    band, sprays = Q.rice_crown(fc, sprays=SPRAYS, **CROWN)
    sc.part("crown-sprays", sprays, sil=False)
    sc.part("crown", band)
    return fc


def figure():
    sc = K.Scene()
    fc = K.face(HEAD, "3/4-left", sex="f", **FACE)
    size = K.hand_size(fc) * HAND_SCALE

    # queen's LEFT (viewer's right): wrap on the sceptre's culm, thumb up, forearm out and down to the cloak edge
    h_sc = K.hand5(GRIP_S, -90.0, "wrap", size=size, hand="L", view="back", grip_w=2 * SCEPTRE_HW)
    sl_sc = sleeve_end(h_sc, run=SCEPTRE_RUN, reach=SCEPTRE_REACH, flare=10.0)
    cuff_sc = sleeved_hand(h_sc, sl_sc)
    sceptre = sceptre_part()

    # queen's RIGHT (viewer's left): wrap on the fan's handle, forearm out and down-left to the cloak edge
    fan_parts = FN.fan(GRIP_F, FAN_AXIS, PLUMES, **FAN_KW)
    h_fn = K.hand5(GRIP_F, FAN_AXIS, "wrap", size=size, hand="R", view="back", grip_w=FAN_HANDLE_W)
    sl_fn = sleeve_end(h_fn, run=FAN_RUN, reach=FAN_REACH, flare=7.0)
    cuff_fn = sleeved_hand(h_fn, sl_fn)
    handle = dict(fan_parts)["handle"]
    held_fn = held_attribute(handle, cuff_fn)

    brooch = K.lion_clasp(BROOCH, 40.0)
    gshape, top = QG.gown_outline()
    plumes = [pt.shape for nm, pt in fan_parts if nm.startswith("plume")]
    ferrule = dict(fan_parts)["ferrule"].shape
    bertha_top = Q.bertha(gshape, top, depth=BERTHA, pearl=PEARL, avoid_gap=4.5,
                          avoid=K.U(brooch.shape, *plumes))
    bertha = K.c2(bertha_top)
    opening, ladder = QG.lacing()

    sleeves = K.U(sl_sc, sl_fn)
    seam = LineString(F.seam_spec(SEAM)["points"])
    front = K.U(sceptre.shape, cuff_sc.shape, held_fn.shape, brooch.shape, *plumes, bertha_top.shape)
    cloak = QG.cloak(front, sleeves=sleeves, seam=seam)
    gown = QG.gown(K.U(bertha.shape, opening, ladder, brooch.shape), soft=K.U(sceptre.shape, cuff_sc.shape, held_fn.shape, sl_sc, sl_fn, ferrule, *plumes),
                   seam=seam)

    sc.part("cloak", cloak)
    sc.part("neck", Q.neck_chest(*NECK, bottom=360.0))
    head_group(sc, fc)
    sc.gown_meta = gown.meta
    sc.part("gown", gown)
    sc.part("opening", K.Part(opening, K.fill(opening, K.RED), K.outline(opening), {}))
    sc.part("lacing", K.Part(ladder, K.fill(ladder, K.GOLD), K.outline(ladder), {}))
    sc.part("bertha", bertha)
    sc.part("brooch", brooch)
    sc.part("sleeve-sceptre", sleeve_part(h_sc, sl_sc, reach=SCEPTRE_REACH))
    sc.part("sleeve-fan", sleeve_part(h_fn, sl_fn, reach=FAN_REACH))
    for nm, pt in fan_parts:
        if nm.startswith("plume"):
            sc.part(nm, pt)
    sc.part("ferrule", dict(fan_parts)["ferrule"])
    sc.part("fan+hand", held_fn)
    # the culm alone carries the silhouette's contour (the head's florets keep MEDIUM outlines)
    sc.add("culm", C.Frag(), sceptre.meta["culm"])
    sc.part("sceptre", sceptre, sil=False)
    sc.part("hand-sceptre", cuff_sc)
    return sc, fc


def build():
    sc, _ = figure()
    return sc.layers()
