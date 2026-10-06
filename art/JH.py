"""J♥ · The Spring Minstrel: flowing robes, one fiddle grip, a tucked bow."""
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
FIST_R = (530.0, 254.0)
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


def figure():
    sc = K.Scene()
    fc = JF.minstrel_profile(HEAD, brow_dy=-16.0, brow_sag=3.0,
                             nostril=(7.5, 0.6, -80.0, 3.4, 160.0))
    collar = JP.collar(H((371, 287)), H((425, 274)), H((361, 308)), H((431, 302)), bot_sag=5.0)
    clasp = K.lion_clasp((388, 333.5), 40)

    # The downward neck axis brings the wrist inward to his shoulder.
    hand = K.hand5(FIST_R, 90, "wrap", size=K.hand_size(fc),
                   hand="L", view="palm", grip_w=17.5)
    base = K.P(hand.wrist) + hand.wrist_dir * 72
    sleeve, _ = K.sleeve(K.SleeveSpec(base=base, wrist=hand.wrist,
                                     width=49, wrist_w=hand.wrist_w,
                                     cuff=0, color=K.JADE, folds=0))
    arm = hand.with_sleeve(sleeve)
    arm = K.Part(arm.shape, K.fill(arm.shape.difference(arm.meta["hand_region"]), K.JADE),
                 arm.lines, arm.meta)
    fd = JP.Fiddle(x=FX, body_top=296, volute="spiral", scroll_r=21.5,
                   pegbox_len=54, peg_t=(0.36, 0.55, 0.70, 0.88),
                   waist=(37, 100), fhole=(22, 92, 24, 140, 2.5), bridge_ext=5,
                   pegs="T", tpeg=(0.5, 9, 8, 10))
    held = JC.fiddle(fd, arm)

    # The bow is upright and parallel, carried under the chest baldric at
    # y330. No second hand or forearm is present; its frog stays above the
    # seam. The panel covers its stick at the fastening, without a halo.
    bow = JP.bow(BX, 112, 384, 422, color=K.GOLD, stick_w=7.4,
                 hair_dx=15, camber=3.5, frog_h=22)
    hair = K.seg((BX + 15, 382.2), (BX + 15, 134), K.RULE, role="bow-hair")
    bow = K.Part(bow.shape, bow.fills,
                 bow.lines.select(lambda m: m.role != "bow-hair") + hair)
    bow = K.Part(bow.shape, JC.merge([bow]).fills, bow.lines)
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
    portrait = JC.merge([face, hair, beret, plume, brooch, collar])
    brim = K.clip_in(K.outline(beret.shape, K.RULE, role="brim-edge"),
                     hair.shape.buffer(1.6))
    portrait = K.Part(portrait.shape, portrait.fills, portrait.lines + brim)
    robes = JC.garments(K.U(held.shape, portrait.shape, bow.shape), clasp)
    # The bow lies in front of the sleeve and under a short paper sash tab.
    tab = robes.meta["tab"]
    bow = K.Part(bow.shape.difference(tab), K.clip_out(bow.fills, tab, eps=0, trap=0),
                 K.clip_out(bow.lines, tab, eps=5, trap=0))
    sc.part("robes", robes)
    sc.part("tucked-bow", bow, sil=False)
    sc.part("fiddle+hand+sleeve", held)
    sc.part("portrait", portrait)
    return sc


def build():
    sc = figure()
    frag = sc.compose(heal_gaps=False)
    bow = next(it.occ for it in sc.items if it.name == "tucked-bow")
    # A carried bow has its own MEDIUM edge, not a heavy silhouette channel.
    contours = K.clip_out(frag.select(lambda m: m.role == "contour"),
                          bow.buffer(K.MEDIUM / 2), eps=0, trap=0)
    frag = frag.select(lambda m: m.role != "contour") + contours
    frag = K.heal(frag, keep_roles=("contour", "brim-edge"))
    frag = JC.trap_under_ink(frag)
    tab = K.R("M230 312 L294 330 L301 349 L237 331 Z")
    # Interlace the printed outlines, not just their centrelines: a clipped
    # round cap must not protrude into the paper fold. Stroke expansion
    # preserves the kit's legal weights while sharing one ink junction.
    edge = K.seg((230, 312), (294, 330), K.MEDIUM)
    edge += K.seg((237, 331), (301, 349), K.MEDIUM)
    patch = K.box(225, 300, 312, 362)
    ink = K.U(frag.shape("ink").intersection(patch).difference(tab),
              edge.shape().intersection(patch))
    pockets = [Polygon(r) for pg in K._polys_of(ink) for r in pg.interiors
               if Polygon(r).area < 30]
    ink = K.U(ink, *pockets)
    strokes = K.clip_out(frag.select(lambda m: m.layer == "ink"), patch, eps=-0.5, trap=0)
    frag = frag.select(lambda m: m.layer != "ink") + strokes + K.fill(ink, K.INK)
    return K.layers(K.heal(frag, keep_roles=("contour", "brim-edge")))
