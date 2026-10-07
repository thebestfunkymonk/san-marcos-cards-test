"""J♥ · The Spring Minstrel: patterned robes and two cuff-emerging grips."""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import Polygon

from deck import courtkit as K
from deck.motifs import core as C
from art import _jh_face as JF
from art import _jh_parts as JP
from art import _jh_head as JH_
from art import _jh_continuous as JC

DOUBLE_HEAD = "continuous"
SEAM = -24
HD = (-6.0, 2.0)
HEAD = (386.0, 208.0)
FX, BX = 512.0, 246.0
FID_DY = 40.0
FIST_R = (FX, 306.0)
FIST_L = (253.0, 392.0)
HAND_S = 0.82
FID_HAND = ("L", "back")
BOW_HAND = ("R", "back")
FID_RUN, FID_REACH, FID_FLARE = 50.0, 0.0, 14.0
BOW_RUN, BOW_REACH, BOW_FLARE = 72.0, 0.0, 12.0
TILT = -5.0
PIVOT = (392.0, 296.0)


def tilt(part):
    """Rigid head tilt, retaining the legal stroke widths."""
    shape = shapely.affinity.rotate(part.shape, TILT, origin=PIVOT)
    return K.Part(shape, part.fills.rotate(TILT, *PIVOT),
                  part.lines.rotate(TILT, *PIVOT), part.meta)


def H(*pts):
    out = [(x + HD[0], y + HD[1]) for x, y in pts]
    return out if len(out) > 1 else out[0]


BERET = H((350, 172), (338, 162), (342, 144), (388, 124), (446, 110), (492, 116), (508, 136), (502, 164),
          (486, 182), (464, 184), (440, 180), (400, 169), (364, 168))
BAND = H((358, 184), (442, 197))
PLUME = H((404, 160), (442, 126), (486, 100), (532, 86), (566, 90), (582, 112))
BOB = H((424, 196), (448, 194), (462, 214), (466, 246), (458, 272), (432, 281), (410, 272), (407, 254),
        (414, 238), (419.5, 222), (420, 208))
BOB_GUIDE = H((432, 188), (450, 212), (454, 244), (446, 274))


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
    # Round the far (elbow) end only; the mouth keeps its crisp corners beside the hand.
    elbow = shape.buffer(-elbow_r).buffer(elbow_r)
    mouth = shape.intersection(Polygon([w - n * 60 - u * 4, w + n * 60 - u * 4,
                                        w + n * 60 + u * 16, w - n * 60 + u * 16]))
    return K.U(elbow, mouth)


def cuff_band(hand_region, sleeve, *, offset=8.0):
    """A bold turn-back line parallel to the cuff mouth, inside the sleeve."""
    edge = hand_region.buffer(offset).boundary.intersection(sleeve.buffer(0.5))
    out = C.Frag()
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 8.0:
            out += K.line(C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def sleeve_edges(sleeve):
    """The sleeve's own folds: its edges run on inside the cloak to the cloak outline."""
    out = C.Frag()
    for g in K._lines_of(K.R(sleeve).boundary):
        out += K.line(C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def sleeve_hatch(hand, sleeve):
    """Hatching along the forearm axis, so the sleeve grain differs from the cloak's."""
    u = hand.wrist_dir
    ang = float(np.degrees(np.arctan2(u[1], u[0])))
    return K.hatch_in(sleeve.buffer(-9.0), angle=ang, origin=tuple(hand.wrist))


def sleeved_hand(hand, sleeve):
    """The hand beyond its cuff mouth; the sleeve's edge is the hand's contour."""
    region = K._biggest(hand.shape.difference(sleeve))
    # The mouth's curl can leave a thin heel tip beside the sleeve; drop it
    # so its paper does not show through the held plate beneath.
    near = sleeve.buffer(10)
    region = K._biggest(K.U(region.difference(near),
                           region.intersection(near).buffer(-2.2).buffer(2.2)))
    inner = hand.hand.meta.get("inner", C.Frag())
    return K.Part(region, C.Frag(), K.outline(region) + K.clip_in(inner, region.buffer(-5.0)),
                  {**hand.hand.meta, "hand_region": region})


def figure():
    sc = K.Scene()
    fc = JF.minstrel_profile(HEAD, brow_dy=-16.0, brow_sag=3.0,
                             pupil_tuck=0.4,
                             nostril=(7.5, 0.6, -80.0, 3.4, 160.0))
    collar = JP.collar(H((371, 287)), H((425, 274)), H((361, 308)), H((431, 302)), bot_sag=5.0)
    clasp = K.lion_clasp((388, 333.5), 40)

    # Both hands are back-view fists, fingers toward the tunic, thumb up the shaft, each forearm
    # running down and outward into a sleeve of the jade cloak (see library/courts.md, JH).
    hand = K.hand5(FIST_R, -90, "wrap", size=K.hand_size(fc) * HAND_S,
                   hand=FID_HAND[0], view=FID_HAND[1], grip_w=17.5)
    fid_sleeve = sleeve_end(hand, run=FID_RUN, reach=FID_REACH, flare=FID_FLARE)
    cuff = sleeved_hand(hand, fid_sleeve)
    fd = JP.Fiddle(x=FX, body_top=296 + FID_DY, volute="spiral", scroll_r=21.5,
                   pegbox_len=54, peg_t=(0.36, 0.55, 0.70, 0.88),
                   waist=(37, 100), fhole=(22, 92, 24, 140, 2.5), bridge_ext=5,
                   pegs="T", tpeg=(0.5, 9, 8, 10))
    held = JC.fiddle(fd, cuff)

    # Restore the original head/frog/button geometry. Shorten only the long
    # stick by 40px so the original frog and button clear the approved seam.
    bow = JP.bow(BX, 112, 414, 450, color=K.GOLD, stick_w=7.4,
                 hair_dx=15, camber=3.5, frog_h=22)
    hair = K.seg((BX + 15, 412.2), (BX + 15, 134), K.RULE, role="bow-hair")
    bow = K.Part(bow.shape, bow.fills,
                 bow.lines.select(lambda m: m.role != "bow-hair") + hair)
    bow = K.Part(bow.shape, JC.merge([bow]).fills, bow.lines)
    second = K.hand5(FIST_L, -90, "wrap", size=K.hand_size(fc) * HAND_S,
                     hand=BOW_HAND[0], view=BOW_HAND[1], grip_w=20, spread=3)
    bow_sleeve = sleeve_end(second, run=BOW_RUN, reach=BOW_REACH, flare=BOW_FLARE)
    bow_cuff = sleeved_hand(second, bow_sleeve)
    bow = JC.held(bow, bow_cuff)
    _, edge = JP.open_spline(H((412, 190), (419, 204), (419.5, 222), (414, 238), (407, 254), (407, 272)))
    behind = Polygon(np.vstack([edge, [H((412, 285)), H((480, 285)), H((480, 150)), H((412, 150))]]))
    collar_up = shapely.affinity.rotate(collar.shape, -TILT, origin=PIVOT)
    hair = tilt(JH_.bob(BOB, BOB_GUIDE,
                       filler=behind.intersection(K.U(fc.skin, K.box(395, 200, 440, 275))),
                       around=(fc.skin, collar_up)))
    face = tilt(K.Part(fc.skin, C.Frag(), fc.lines + K.outline(fc.head)))
    neck_keep = K.box(0, 0, 750, 310)
    face = K.Part(face.shape.intersection(neck_keep), C.Frag(),
                  K.clip_in(face.lines, neck_keep))
    beret = tilt(JH_.soft_beret(BERET, BAND, 18, fc.skin, ripple=(14, 1.6),
                               under_hatch=14, under_x1=482))
    plume = tilt(JP.plume_locks(PLUME, n=4, ends=(1, 0.92, 0.84, 0.76),
                                tip_curl=(12, 200), curl_deg=110, smooth=10))
    brooch = tilt(JP.fluke_heart((PLUME[0][0] + 1, PLUME[0][1] - 3.7),
                                 u=17, bezel=7.4, ring=3))
    crown = beret.shape.buffer(-8).difference(
        K.U(plume.shape, brooch.shape, beret.lines.shape()).buffer(7.3))
    beret.lines += K.hatch_in(crown, angle=-35, origin=(375, 140))
    portrait = JC.merge([face, hair, beret, plume, brooch, collar])
    brim = K.clip_in(K.outline(beret.shape, K.RULE, role="brim-edge"),
                     hair.shape.buffer(1.6))
    portrait = K.Part(portrait.shape, portrait.fills, portrait.lines + brim)
    robes = JC.garments(K.U(held.shape, portrait.shape, bow.shape), clasp,
                        sleeves=K.U(fid_sleeve, bow_sleeve),
                        sleeve_grain=sleeve_hatch(hand, fid_sleeve) + sleeve_hatch(second, bow_sleeve),
                        cuff_bands=cuff_band(cuff.shape, fid_sleeve)
                        + cuff_band(bow_cuff.shape, bow_sleeve)
                        + sleeve_edges(fid_sleeve) + sleeve_edges(bow_sleeve))
    sc.part("robes", robes)
    sc.part("bow+hand+cuff", bow, sil=False)
    sc.part("fiddle+hand+cuff", held)
    sc.part("portrait", portrait)
    return sc


def build():
    sc = figure()
    frag = sc.compose(heal_gaps=False)
    bow = next(it.occ for it in sc.items if it.name == "bow+hand+cuff")
    # A carried bow has its own MEDIUM edge, not a heavy silhouette channel.
    contours = K.clip_out(frag.select(lambda m: m.role == "contour"),
                          bow.buffer(K.MEDIUM / 2), eps=0, trap=0)
    frag = frag.select(lambda m: m.role != "contour") + contours
    # Heal twice: the second pass trims outline strokes that the first still reports.
    frag = K.heal(K.heal(frag, keep_roles=("contour", "brim-edge", "cuffline")),
                  keep_roles=("contour", "brim-edge", "cuffline"))
    return K.layers(K.heal(frag, keep_roles=("contour", "brim-edge", "cuffline")))
