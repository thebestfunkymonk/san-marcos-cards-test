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
FX, BX = 530.0, 246.0
FIST_R = (530.0, 280.0)
FIST_L = (253.0, 380.0)
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


def fold_cuff(hand, depth=24):
    """A patterned opening, not a shoulder-to-hand sleeve."""
    w, u = K.P(hand.wrist), hand.wrist_dir
    n = np.array([u[1], -u[0]])
    hw = (hand.wrist_w + 10) / 2
    base = w + u * depth
    shape = K.R(K.Path(w - u * 2 + n * hw).line(w - u * 2 - n * hw)
                .sag(base - n * (hw + 2), -2).line(base + n * (hw + 2))
                .sag(w - u * 2 + n * hw, -2).close().d).buffer(-1.6).buffer(1.6)
    hatch = K.hatch_in(shape.buffer(-4),
                       angle=float(np.degrees(np.arctan2(u[1], u[0]))) + 45,
                       origin=tuple(base))
    cuff = K.Part(shape, K.fill(shape, K.JADE), hatch)
    joined = hand.with_sleeve(cuff, cuff_line=True)
    jade = joined.shape.difference(joined.meta["hand_region"])
    return K.Part(joined.shape, K.fill(jade, K.JADE), joined.lines,
                  {**joined.meta, "cuff_depth": depth, "cuff_width": 2 * hw})


def figure():
    sc = K.Scene()
    fc = JF.minstrel_profile(HEAD, brow_dy=-16.0, brow_sag=3.0,
                             pupil_tuck=0.4,
                             nostril=(7.5, 0.6, -80.0, 3.4, 160.0))
    collar = JP.collar(H((371, 287)), H((425, 274)), H((361, 308)), H((431, 302)), bot_sag=5.0)
    clasp = K.lion_clasp((388, 333.5), 40)

    # Both wrists disappear immediately into local folds beside the objects.
    hand = K.hand5(FIST_R, 90, "wrap", size=K.hand_size(fc) * 0.82,
                   hand="R", view="palm", grip_w=17.5)
    cuff = fold_cuff(hand)
    fd = JP.Fiddle(x=FX, body_top=296, volute="spiral", scroll_r=21.5,
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
    second = K.hand5(FIST_L, -90, "wrap", size=K.hand_size(fc) * 0.82,
                     hand="R", view="back", grip_w=20, spread=3)
    bow = JC.held(bow, fold_cuff(second))
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
    robes = JC.garments(K.U(held.shape, portrait.shape, bow.shape), clasp)
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
    # Unite the jade cuff and mantle plates before healing their contact.
    jade = K.U(*[K.R(m.d) for m in frag.marks
                 if m.kind == "fill" and m.color == K.JADE])
    gold = K.U(*[K.R(m.d) for m in frag.marks
                 if m.kind == "fill" and m.color == K.GOLD])
    contact = K.box(480, 292, 523, 312)
    jade = K.U(jade, jade.buffer(3).buffer(-3).intersection(contact)).difference(
        gold.buffer(-0.4).intersection(contact))
    frag = frag.select(lambda m: not (m.kind == "fill" and m.color == K.JADE))
    frag += K.fill(jade, K.JADE)
    frag = K.heal(frag, keep_roles=("contour", "brim-edge"))
    frag = JC.trap_under_ink(frag)
    return K.layers(K.heal(frag, keep_roles=("contour", "brim-edge")))
