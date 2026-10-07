"""K♥ · The Ferryman King: continuous textiles and two cuff-emerging hands."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from art import _kh_head as KHH
from art import _kh_parts as KP
from art import _kh_continuous as KC

DOUBLE_HEAD = "continuous"
SEAM = -20
AX = K.AX
HEAD = (AX, 207.0)
# The king's left hand (viewer's right) holds the pole from the cloak side: back view, thumb
# toward the pole's upper end, fingers wrapped round the far side toward the tunic. The pole
# is steeper than before so the forearm leaves the wrist outward and slightly down.
FIST = (500.0, 470.0)
POLE_DEG = -112.0
POLE_TOP = (FIST[0] + 436.0 * float(np.cos(np.radians(POLE_DEG))),
            FIST[1] + 436.0 * float(np.sin(np.radians(POLE_DEG))))
POLE_BUTT = (FIST[0] - 28.0 * float(np.cos(np.radians(POLE_DEG))),
             FIST[1] - 28.0 * float(np.sin(np.radians(POLE_DEG))))
POLE_HAND = ("L", "back")
POLE_RUN = 84.0
POLE_REACH = 11.0
CHAL_RUN = 70.0
CHAL_REACH = 12.0
FACE_KW = dict(age="elder", lids="level", lid_sag=5.4, low_sag=3.0, brow_sag=5.0, brow_dy=-14.0,
               brow_drop=3.0, bow_rise=0.4, bow_sag=-2.2, lip_sag=-2.6, lip_hw=6.5)
HAIR = K.HairSpec(bulge=(-64.0, 34.0), bottom=(-52.0, 66.0), ribbons=4, over=12.0)
MOUSTACHE = KHH.LiftMoustache(tip=(-30.0, 9.0), arch=3.4, under=5.6)
BEARD = KHH.LobeBeard()
BEARD_LOCKS = {"mode": "manual", "locks": [
    ((-36.0, 30.0), (-41.4, 57.0), (-38.5, 81.0), -180.0, 4.8),
    ((-19.0, 76.0), (-18.4, 89.0), (-14.5, 99.0), -180.0, 4.0)]}
POLE_WIDTH = 18.0
CHAL_X = 233.5
CHAL_RIM = 292.0
CHAL_GRIP = (CHAL_X, 392.0)
HAND_SCALE = 0.82


class Scene(KP.Scene):
    """Keep the regalia plate joined and seal trapped background pinholes."""
    def compose(self, *, heal_gaps=True, **kwargs):
        artwork = super().compose(heal_gaps=False, **kwargs)
        gold = artwork.select(lambda m: m.kind == "fill" and m.layer == "gold")
        gold_plate = gold.shape().buffer(0.6).buffer(-0.6)
        artwork = artwork.select(lambda m: not (m.kind == "fill" and m.layer == "gold")) \
            + K.fill(gold_plate, K.GOLD)
        if heal_gaps:
            self.heal_log = []
            artwork = K.heal(artwork, log=self.heal_log, keep_roles=("contour", "grip-edge"))
        contour_roles = ("contour", "grip-edge")
        contour = artwork.select(lambda m: m.layer == "ink" and m.role in contour_roles)
        # Print one unioned outline plate, not overlapping contour fragments.
        # Do this after healing: filled outline rings must retain their holes.
        artwork = artwork.select(lambda m: not (m.layer == "ink" and m.role in contour_roles)) \
            + K.fill(contour.shape().buffer(0.35).buffer(-0.35), K.INK, role="contour")
        ink = artwork.select(lambda m: m.layer == "ink").shape()
        # A closed sub-pixel hole in a shared outline is not a garment detail.
        # Stroke its boundary into the surrounding ink, without changing hand5.
        for pg in K._polys_of(ink):
            for ring in pg.interiors:
                hole = Polygon(ring)
                if hole.area < 1.6:
                    artwork += K.outline(hole, role="contour")
        return artwork


def sleeve_end(hand, *, run, reach=0.0, cuff=3.0, flare=14.0, curl=5.0):
    """The cloak's own sleeve: a bell that opens from the cuff mouth toward the elbow, running
    past the cloak's outer edge so the garment outline is the sleeve's outer end."""
    u = hand.wrist_dir
    w = K.P(hand.wrist) - u * reach
    n = np.array([u[1], -u[0]])
    half = hand.wrist_w / 2
    base = w + u * run
    shape = K.R(K.Path(w + n * (half + cuff)).sag(w - n * (half + cuff), curl)
                .sag(base - n * (half + cuff + flare), 1.5).line(base + n * (half + cuff + flare))
                .sag(w + n * (half + cuff), 1.5).close().d)
    return shape


def cuff_band(hand, sleeve, *, reach, offset=9.0, cuff=3.0, curl=5.0):
    """A fine turn-back line parallel to the cuff mouth, inside the sleeve."""
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


def sleeve_stripes(hand, sleeve, *, start=20.0, inset=4.8, fans=(-0.6, 0.0, 0.6)):
    """Cream pleats fanning from the cuff toward the elbow, knocked out of the red."""
    u = hand.wrist_dir
    n = np.array([u[1], -u[0]])
    mouth = K.P(hand.wrist)
    half = hand.wrist_w / 2 + 3.0
    out = K.C.Frag()
    zone = sleeve.buffer(-inset)
    for f in fans:
        a = mouth + u * start + n * (f * half * 1.2)
        b = mouth + u * 160.0 + n * (f * half * 3.4)
        seg = LineString([a, b]).intersection(zone)
        for g in K._lines_of(seg):
            if g.length > 12.0:
                out += K.line(K.C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="pleat")
    return out


def sleeved_hand(hand, sleeve):
    """The hand beyond its cuff mouth; the sleeve's edge is the hand's contour."""
    region = K._biggest(hand.shape.difference(sleeve))
    inner = hand.hand.meta.get("inner", K.C.Frag())
    return K.Part(region, K.C.Frag(), K.outline(region) + K.clip_in(inner, region.buffer(-5.0)),
                  {**hand.hand.meta, "hand_region": region})


def held_attribute(attribute, hand_cuff):
    """One outline at the hand, cuff and held shaft, without a halo."""
    # A small join fillet belongs to the union, not to the shared hand asset.
    shape = K.U(attribute.shape, hand_cuff.shape).buffer(1.6).buffer(-1.6).simplify(0.02)
    # Trap the held plate beneath the grip outline, rather than eroding
    # thin ends beside a thumb into little paper wedges.
    fills = K.clip_in(attribute.fills, attribute.shape.difference(
        hand_cuff.shape.buffer(-K.MEDIUM / 2))) + hand_cuff.fills
    return K.Part(
        shape,
        fills,
        K.clip_out(attribute.lines.select(lambda m: m.role != "outline"), hand_cuff.shape,
                   eps=0.2, trap=0.0)
        + hand_cuff.lines.select(lambda m: m.role != "outline")
        + K.clip_in(K.outline(hand_cuff.shape, role="grip-edge"), attribute.shape.buffer(2.0))
        + K.outline(shape, role="contour"), hand_cuff.meta)


def figure():
    fc = K.face(HEAD, "frontal", **FACE_KW)
    hair = [K.hair_fall(fc, s, HAIR) for s in (-1, 1)]
    mo = KHH.moustache(fc, MOUSTACHE)
    beard = KHH.lobe_beard(fc, BEARD, mo=mo, lines=BEARD_LOCKS)
    # Foreground edges must stay whole; texture healing must not turn the
    # hair/robe junction into detached rounded contour fragments.
    for part in [*hair, beard]:
        part.lines = part.lines.select(lambda m: m.role != "outline") + K.outline(part.shape, role="contour")
    h = K.hand5(FIST, POLE_DEG, "wrap", size=K.hand_size(fc) * HAND_SCALE,
                hand=POLE_HAND[0], view=POLE_HAND[1], grip_w=POLE_WIDTH)
    right_sleeve = sleeve_end(h, run=POLE_RUN, reach=POLE_REACH)
    right_cuff = sleeved_hand(h, right_sleeve)
    # The king's right hand (viewer's left) grips the stem: fingers toward the tunic, thumb up
    # toward the bowl, forearm down and out into the cloak's left edge.
    left = K.hand5(CHAL_GRIP, -90.0, "wrap", size=K.hand_size(fc) * HAND_SCALE,
                   hand="R", view="back", grip_w=10.4, spread=4.0)
    left_sleeve = sleeve_end(left, run=CHAL_RUN, reach=CHAL_REACH, flare=7.0)
    left_cuff = sleeved_hand(left, left_sleeve)
    u = K.unit(POLE_DEG)
    pole = KP.pole(K.P(POLE_BUTT), K.P(POLE_TOP) + u * 40.0, w=POLE_WIDTH,
                   round_low=True, bands_y=tuple(range(84, 370, 44)), wraps=((378.0, 412.0),))
    held = held_attribute(pole, right_cuff)
    # Restore the original bowl, engraved vent, knop and bell foot.
    chalice = KP.chalice(CHAL_X, CHAL_RIM, rim_hw=29.0, bowl_h=44.0, stem_len=90.0,
                         foot_hw=(7.0, 21.5), tip_r=2.2, engrave_gap=4.3)
    cup = held_attribute(chalice, left_cuff)
    by = CHAL_RIM - 12.0
    bubbles = KP.bubble_column(
        [(CHAL_X - 2, by), (CHAL_X - 6, by - 15), (CHAL_X - 11, by - 33),
         (CHAL_X - 17, by - 54), (CHAL_X - 24, by - 79)],
        [6.3, 8.4, 10.5, 12.6, 15.2])
    crown = KC.crown()
    neckline = K.U(*[p.shape for p in hair], beard.shape)
    # The sleeves belong to the lapel, so its outline and scales run on into
    # them. The complete hand is kept out: closing around it would spill jade
    # into its distal finger webs.
    garment = KC.garments(K.U(held.shape, cup.shape, bubbles.shape, neckline),
                          neckline, K.U(right_sleeve, left_sleeve),
                          pocket_front=K.U(cup.shape, held.shape),
                          cuff_bands=cuff_band(h, right_sleeve, reach=POLE_REACH) + cuff_band(left, left_sleeve, reach=CHAL_REACH),
                          skim=pole.shape, sleeve_stripes=sleeve_stripes(h, right_sleeve) + sleeve_stripes(left, left_sleeve))
    sc = Scene(over_contour={"crown": 1.6}, stroke_ends={"crown": 1.6})
    collar = K.standing_collar(top_y=231.0, half_w=112.0, neck_y=262.0,
                               shoulder=(-130.0, 304.0), side_sag=-3.0, rim=9.5,
                               color=K.JADE, rim_color=K.RED)
    collar.lines = K.C.Frag([replace(m, role="contour") if m.role == "fold" else m
                             for m in collar.lines.marks])
    collar.lines += K.hatch_in(collar.shape.difference(collar.meta["rim"]).buffer(-7.0)
                              .difference(neckline.buffer(7.3)),
                              origin=(K.AX, 262.0))
    sc.part("collar", collar)
    sc.part("robes", garment)
    sc.part("pole+handR+cuff", held)
    sc.part("chalice+handL+cuff", cup)
    sc.part("bubbles", bubbles, sil=False)
    for s, p in zip((-1, 1), hair):
        sc.part(f"hair{s}", p)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("beard", beard + mo)
    sc.part("crown", crown, sil=False)
    return sc


def build():
    return figure().layers()
