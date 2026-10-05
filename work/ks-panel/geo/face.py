"""The §H.0 face kit, constructed with compass and ruler.

One function draws every court face in the deck:

    face(FaceSpec(...)) -> Face(head=d, skin=region, lines=Frag, meta)

Construction (frontal; the left half is drawn and mirrored about the axis):

* Head   — a Moss egg of radius r (88 × 113.8 at r 44): a circle, two arcs of
           radius 2r struck from the ends of its horizontal diameter, and a
           chin arc of radius r(2 − √2).
* Eye    — a vesica 24 × 10 (two arcs of equal radius): the upper arc is the
           RULE lid, the lower arc the FINE lid; a Ø6.3 pupil tucked 0.6 px
           under the lid for the heavy-lidded, level gaze.
* Brow   — one MEDIUM arc given by chord + sagitta.
* Nose   — a straight MEDIUM ridge ending in a small hook (a tangent arc of
           radius ``hook_r``) that turns out into the nostril wing.
* Mouth  — the two-arc upper-lip bow (two arcs meeting in a cusp on the axis)
           and a FINE lower-lip tick (one arc).
* Ear    — a C (a 200° arc), optional (hair usually covers it).

Stroke count (frontal): brows 2, upper lids 2, lower lids 2, pupils 2,
nose 2, lip bow 1, lower lip 1 = 12; optional cheek arcs 2 (age) or ears 2,
never both: ≤ 14.

3/4 faces (``turn`` = ±1, toward the viewer's right/left): the feature axis
shifts 12 % of the head width toward the turn, the far eye is 70 % wide, the
nose is one ridge on the far side of the axis. Profiles are out of scope for
this module (their silhouettes are drawn per court).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

import kit as K
from deck.motifs import core as C


@dataclass
class FaceSpec:
    cx: float = 375.0
    head_cy: float = 206.0      # centre of the egg's circle (its widest line)
    head_r: float = 44.0
    eye_y: float = 213.0
    eye_dx: float = 21.0        # eye centre offset from the feature axis
    eye_w: float = 24.0
    eye_h: float = 10.0
    lid_sag: float = 3.6        # upper lid sagitta (flatter than the lower: the hooded, heavy lid)
    low_sag: float = 5.0        # lower lid sagitta
    pupil_d: float = 6.3
    pupil_dy: float = 0.9       # pupil centre relative to the eye centre line (tucked under the lid)
    brow_y: float = 200.0       # brow inner end y
    brow_in: float = 7.0        # inner end offset from the axis
    brow_out: float = 35.0      # outer end offset from the axis
    brow_drop: float = 1.5      # outer end lower than the inner by
    brow_sag: float = 3.2
    nose_dx: float = 6.0        # ridge offset from the axis at the bottom (frontal: both sides)
    nose_dx_top: float = 3.6    # ...and at the top (the ridges converge toward the brow)
    nose_top: float = 208.0
    nose_bot: float = 240.0
    hook_r: float = 4.2
    hook_sweep: float = 150.0
    mouth_y: float = 261.0      # y of the mouth corners
    mouth_hw: float = 11.0
    bow_rise: float = 1.8       # centre cusp higher than the corners by
    bow_sag: float = -1.6       # each half bows down (negative = right of travel)
    lip_y: float = 268.0
    lip_hw: float = 5.5
    lip_sag: float = -1.8
    ears: bool = False
    mouth_bow: bool = True      # False when a moustache's lower edge is the lip line
    cheeks: bool = False        # age: a short MEDIUM arc under each eye's outer half (2 strokes)
    cheek_dy: float = 13.0      # below the eye line
    cheek_x: tuple = (13.0, 31.0)   # from/to offset from the axis
    cheek_sag: float = -2.2
    turn: float = 0.0           # 0 frontal; +1 3/4 toward viewer's right, -1 left
    lid_w: float = K.RULE
    feature_w: float = K.MEDIUM


@dataclass
class Face:
    head: str
    skin: object
    lines: C.Frag
    meta: dict


def _half_features(s: FaceSpec, ax: float, eye_scale: float = 1.0, side: int = -1, nose: bool = True):
    """Features of one half (side −1 = viewer's left of ``ax``)."""
    f = C.Frag()
    sg = side
    ex = ax + sg * s.eye_dx * (1 if eye_scale == 1 else 1)
    ew = s.eye_w * eye_scale
    outer = K.P(ex + sg * ew / 2, s.eye_y)
    inner = K.P(ex - sg * ew / 2, s.eye_y)
    # draw left→right so "left of travel" is up
    a, b = (outer, inner) if sg < 0 else (inner, outer)
    f += K.line(K.arc_sag(a, b, s.lid_sag), s.lid_w)                        # upper lid (RULE)
    f += K.line(K.arc_sag(a, b, -s.low_sag), K.FINE)                        # lower lid (FINE)
    f += K.dot((ex, s.eye_y + s.pupil_dy), s.pupil_d)                       # pupil
    # brow
    bi = K.P(ax + sg * s.brow_in, s.brow_y)
    bo = K.P(ax + sg * (s.brow_in + (s.brow_out - s.brow_in) * eye_scale), s.brow_y + s.brow_drop)
    a, b = (bo, bi) if sg < 0 else (bi, bo)
    f += K.line(K.arc_sag(a, b, s.brow_sag), s.feature_w)
    if nose:
        f += nose_line(s, ax, sg)
    if s.cheeks:
        c0 = K.P(ax + sg * s.cheek_x[0] * eye_scale, s.eye_y + s.cheek_dy - 1.5)
        c1 = K.P(ax + sg * s.cheek_x[1] * eye_scale, s.eye_y + s.cheek_dy + 1.5)
        a, b = (c1, c0) if sg < 0 else (c0, c1)
        f += K.line(K.arc_sag(a, b, s.cheek_sag), s.feature_w)
    return f


def nose_line(s: FaceSpec, ax: float, sg: int) -> C.Frag:
    """Straight ridge from (ax ± nose_dx_top, nose_top) to (ax ± nose_dx,
    nose_bot) — the two ridges converge toward the brow — then the hook: a
    tangent arc of radius hook_r turning outward (toward ``sg``) and back up."""
    p0 = K.P(ax + sg * s.nose_dx_top, s.nose_top)
    p1 = K.P(ax + sg * s.nose_dx, s.nose_bot)
    t = C.Turtle(p0[0], p0[1], 0.0)
    t.line_to(p1[0], p1[1])
    t.arc(s.hook_r, s.hook_sweep if sg < 0 else -s.hook_sweep)
    return K.line(t.d(), s.feature_w)


def mouth(s: FaceSpec, ax: float, hw_l: float, hw_r: float) -> C.Frag:
    cusp = K.P(ax, s.mouth_y - s.bow_rise)
    lc, rc = K.P(ax - hw_l, s.mouth_y), K.P(ax + hw_r, s.mouth_y)
    d = K.arc_sag(lc, cusp, s.bow_sag) + K.arc_sag(cusp, rc, s.bow_sag, move=False)
    f = K.line(d, s.feature_w) if s.mouth_bow else C.Frag()
    f += K.line(K.arc_sag(K.P(ax - s.lip_hw, s.lip_y), K.P(ax + s.lip_hw, s.lip_y), s.lip_sag), K.FINE)
    return f


def ear(s: FaceSpec, sg: int) -> C.Frag:
    c = K.P(s.cx + sg * (s.head_r - 1), s.eye_y + 12)
    a0, a1 = (100, 260) if sg < 0 else (-80, 80)
    return K.line(K.arc_c(c, 9.0, a0, a1), s.feature_w)


def face(s: FaceSpec = FaceSpec()) -> Face:
    head, info = K.moss_egg((s.cx, s.head_cy), s.head_r)
    skin = K.R(head)
    lines = C.Frag()
    if s.turn == 0:
        half = _half_features(s, s.cx, 1.0, -1)
        lines += K.bi(half, s.cx)
        lines += mouth(s, s.cx, s.mouth_hw, s.mouth_hw)
        if s.ears:
            lines += ear(s, -1) + ear(s, +1)
        ax = s.cx
    else:
        tsg = 1 if s.turn > 0 else -1
        ax = s.cx + tsg * 0.12 * 2 * s.head_r
        # near eye full width on the side away from the turn, far eye 70 %
        lines += _half_features(s, ax, 1.0, -tsg, nose=False)
        lines += _half_features(s, ax, 0.7, tsg, nose=False)
        lines += nose_line(s, ax, tsg)
        lines += mouth(s, ax, s.mouth_hw * (1.0 if tsg > 0 else 0.75), s.mouth_hw * (0.75 if tsg > 0 else 1.0))
        if s.ears:
            lines += ear(s, -tsg)
    return Face(head=head, skin=skin, lines=lines, meta={**info, "axis": ax})
