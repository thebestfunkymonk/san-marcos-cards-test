"""K♥ · The Ferryman King: continuous textiles and two cuff-emerging hands."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import shapely
from shapely.geometry import Polygon

from deck import courtkit as K
from art import _kh_head as KHH
from art import _kh_parts as KP
from art import _kh_continuous as KC

DOUBLE_HEAD = "continuous"
SEAM = -20
AX = K.AX
HEAD = (AX, 207.0)
FIST = (527.4, 467.9)
POLE_TOP = (271.5, 55.0)
POLE_BUTT = (543.2, 493.4)
POLE_DEG = float(np.degrees(np.arctan2(POLE_TOP[1] - 456.0, POLE_TOP[0] - 520.0)))
# The palm lies on the tunic side of the shaft, so the sleeve is the jade lapel.
POLE_HAND_DEG = POLE_DEG + 180.0
POLE_HAND = ("R", "back")
POLE_RUN = 40.0
POLE_REACH = 16.0
CHAL_RUN = 40.0
CHAL_REACH = 20.0
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
CHAL_GRIP = (CHAL_X, 394.0)
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


def sleeve_end(hand, *, run, reach=0.0, bell=11.0, neck=4.0, curl=5.0):
    """The jade lapel's sleeve: a short bell running from the cuff mouth back
    toward the tunic, so it is the garment's own region and not a separate cuff."""
    u = hand.wrist_dir
    w = K.P(hand.wrist) - u * reach
    n = np.array([u[1], -u[0]])
    half = hand.wrist_w / 2
    base = w + u * run
    shape = K.R(K.Path(w + n * (half + bell)).sag(w - n * (half + bell), curl)
                .sag(base - n * (half + neck), -2.0).line(base + n * (half + neck))
                .sag(w + n * (half + bell), -2.0).close().d)
    return shape.buffer(-1.6).buffer(1.6)


def cuff_band(hand_region, sleeve, *, offset=8.0):
    """A fine turn-back line parallel to the cuff mouth, inside the sleeve."""
    edge = hand_region.buffer(offset).boundary.intersection(sleeve.buffer(0.5))
    out = K.C.Frag()
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 8.0:
            out += K.line(K.C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
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
    shape = K.U(attribute.shape, hand_cuff.shape).buffer(1.6).buffer(-1.6).simplify(0.2)
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
    h = K.hand5(FIST, POLE_HAND_DEG, "wrap", size=K.hand_size(fc) * HAND_SCALE, hand=POLE_HAND[0],
                view=POLE_HAND[1], grip_w=POLE_WIDTH)
    right_sleeve = sleeve_end(h, run=POLE_RUN, reach=POLE_REACH)
    right_cuff = sleeved_hand(h, right_sleeve)
    left = K.hand5(CHAL_GRIP, -90.0, "wrap", size=K.hand_size(fc) * HAND_SCALE,
                   hand="L", view="back", grip_w=10.4, spread=4.0)
    left_sleeve = sleeve_end(left, run=CHAL_RUN, reach=CHAL_REACH, bell=5.0)
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
                          neckline, K.U(right_sleeve, left_sleeve, chalice.shape),
                          pocket_front=K.U(cup.shape, held.shape),
                          cuff_bands=cuff_band(right_cuff.shape, right_sleeve) + cuff_band(left_cuff.shape, left_sleeve))
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
