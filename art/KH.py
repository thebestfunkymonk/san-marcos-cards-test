"""K♥ · The Ferryman King: continuous robes, one hand on the punting pole."""
from __future__ import annotations

import numpy as np

from deck import courtkit as K
from art import _kh_head as KHH
from art import _kh_parts as KP
from art import _kh_continuous as KC

DOUBLE_HEAD = "continuous"
SEAM = -20
AX = K.AX
HEAD = (AX, 207.0)
FIST = (520.0, 456.0)
POLE_TOP = (271.5, 55.0)
POLE_DEG = float(np.degrees(np.arctan2(POLE_TOP[1] - FIST[1], POLE_TOP[0] - FIST[0])))
FACE_KW = dict(age="elder", lids="level", lid_sag=5.4, low_sag=3.0, brow_sag=5.0, brow_dy=-14.0,
               brow_drop=3.0, bow_rise=0.4, bow_sag=-2.2, lip_sag=-2.6, lip_hw=6.5)
HAIR = K.HairSpec(bulge=(-64.0, 34.0), bottom=(-52.0, 66.0), ribbons=4, over=12.0)
MOUSTACHE = KHH.LiftMoustache(tip=(-30.0, 9.0), arch=3.4, under=5.6)
BEARD = KHH.LobeBeard()
BEARD_LOCKS = {"mode": "manual", "locks": [
    ((-36.0, 30.0), (-41.4, 57.0), (-38.5, 81.0), -180.0, 4.8),
    ((-19.0, 76.0), (-18.4, 89.0), (-14.5, 99.0), -180.0, 4.0)]}
POLE_WIDTH = 18.0


def figure():
    fc = K.face(HEAD, "frontal", **FACE_KW)
    hair = [K.hair_fall(fc, s, HAIR) for s in (-1, 1)]
    mo = KHH.moustache(fc, MOUSTACHE)
    beard = KHH.lobe_beard(fc, BEARD, mo=mo, lines=BEARD_LOCKS)
    h = K.hand5(FIST, POLE_DEG, "wrap", size=K.hand_size(fc), hand="R", view="palm",
                grip_w=POLE_WIDTH)
    # The elbow is above the grip, under the right shoulder, not below a divider.
    base = K.P(h.wrist) + h.wrist_dir * 94.0
    sleeve, _ = K.sleeve(K.SleeveSpec(wrist=h.wrist, base=base, width=74.0,
                                     wrist_w=h.wrist_w, cuff=0.0, color=K.JADE, folds=0))
    arm = h.with_sleeve(sleeve)
    arm = K.Part(arm.shape, K.fill(arm.shape.difference(arm.meta["hand_region"]), K.JADE),
                 arm.lines, arm.meta)
    u = K.unit(POLE_DEG)
    pole = KP.pole(K.P(FIST) - u * 44.0, K.P(POLE_TOP) + u * 40.0, w=POLE_WIDTH,
                   round_low=True, bands_y=(84.0, 352.0), wraps=((378.0, 412.0),))
    held_shape = K.U(pole.shape, arm.shape)
    held = K.Part(
        held_shape,
        K.clip_out(pole.fills, arm.shape, eps=0.0, trap=0.0) + arm.fills,
        K.clip_out(pole.lines.select(lambda m: m.role != "outline"), arm.shape,
                   eps=0.2, trap=0.0)
        + arm.lines.select(lambda m: m.role != "outline")
        + K.clip_in(K.outline(arm.shape, role="grip-edge"), pole.shape.buffer(0.2))
        + K.outline(held_shape))
    crown = KC.crown()
    neckline = K.U(*[p.shape for p in hair], beard.shape)
    garment = KC.garments(K.U(pole.shape, arm.shape, neckline), neckline, arm.shape)

    sc = KP.Scene(over_contour={"crown": 1.6}, stroke_ends={"crown": 1.6})
    sc.part("collar", K.standing_collar(top_y=231.0, half_w=112.0, neck_y=262.0,
                                       shoulder=(-130.0, 304.0), side_sag=-3.0, rim=9.5,
                                       color=K.JADE, rim_color=K.RED))
    sc.part("robes", garment)
    sc.part("pole+handR+sleeve", held)
    for s, p in zip((-1, 1), hair):
        sc.part(f"hair{s}", p)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("beard", beard + mo)
    sc.part("crown", crown, sil=False)
    return sc


def build():
    return figure().layers()
