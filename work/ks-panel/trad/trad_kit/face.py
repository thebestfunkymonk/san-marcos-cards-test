"""§H.0 face kit — one hand for all twelve faces.

    spec = FaceSpec(cx=375, eye_y=208)          # frontal king
    spec = FaceSpec(cx=385, eye_y=210, turn=-1)  # 3/4 turned to viewer's left
    outline = face_outline(spec)                 # shapely egg (skin = paper)
    feats   = face_features(spec)                # Frag: <= 14 strokes + pupils

Construction (brief §H.0):
* eyes    vesicas ≈24 × 10 (here two arcs of unequal rise so the lower lid is
          fuller — the heavy-lidded look) with a Ø6 pupil dot tucked up under
          the lid; upper lid RULE 4.2, lower lid FINE 2.1; optional FINE crease.
* brow    one MEDIUM arc.
* nose    frontal: two straight MEDIUM ridges from the brow ends, each ending
          in a small outward hook (the alar wing), plus a short tip arc —
          symmetric by construction. 3/4: one ridge on the far side + hook.
* mouth   a two-arc upper-lip bow (MEDIUM) + a FINE lower-lip tick.
* ear     a C (MEDIUM), optional (hidden under hair on the kings).
Frontal faces are drawn as one half and mirrored. For 3/4 (``turn`` = ±1)
the features shift 12 % of the face width toward the turn and the far eye
is 70 % wide.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

from deck import tokens as T
from deck.motifs import core as MC
from deck.motifs.core import Frag

from . import shapes as SH


@dataclass
class FaceSpec:
    cx: float = 375.0
    eye_y: float = 208.0
    # head (egg-oval)
    top: float = 158.0          # hairline (hidden under crown/hair)
    chin: float = 284.0
    half_w: float = 50.0        # at the cheekbones
    # eyes
    eye_dx: float = 22.0        # half the distance between eye centres
    eye_w: float = 24.0
    lid_rise: float = 4.2       # upper-lid arc rise above the corners (flat = heavy)
    lid_dip: float = 7.0        # lower-lid dip below the corners
    pupil_d: float = 6.0
    pupil_up: float = 1.3       # pupil centre above the corner line (tucked under the lid)
    tilt: float = 0.0           # outer corner raised (+) / lowered (-) px
    crease: bool = True         # FINE lid crease (weight of age)
    crease_gap: float = 7.6     # centreline gap lid -> crease
    # brows
    brow_gap: float = 9.0       # brow centre above the crease/lid
    brow_in: float = 3.0        # inner end x-offset from the eye's inner corner (toward axis)
    brow_out: float = 5.0       # outer overshoot past the outer corner
    brow_rise: float = 4.0
    brow_slope: float = 1.5     # inner end lower than the outer (stern level gaze)
    # nose
    bridge: float = 6.5         # half-width of the bridge (ridge x offset from cx)
    nose_top: float | None = None
    nose_len: float = 31.0      # from eye line to the nostril hook
    hook_r: float = 4.2
    tip_w: float = 5.0          # half-width of the tip arc
    # mouth
    mouth_y: float = 258.0
    mouth_w: float = 15.0       # half-width
    bow: float = 2.6            # cupid's-bow depth
    lower_lip: float = 8.0      # lower-lip tick below the mouth line
    lower_w: float = 6.5
    # ears
    ear: bool = False
    ear_y: float = 214.0
    ear_h: float = 26.0
    # 3/4
    turn: float = 0.0           # -1 viewer's left, +1 viewer's right, 0 frontal


def _half(cx, top, chin, hw, sgn, chin_dx=0.0):
    H = chin - top
    pts = [(cx, top), (cx + sgn * hw * 0.80, top + 0.10 * H), (cx + sgn * hw, top + 0.38 * H),
           (cx + sgn * hw * 0.93, top + 0.62 * H), (cx + sgn * hw * 0.66, top + 0.84 * H),
           (cx + chin_dx + sgn * hw * 0.28, chin - 1.5), (cx + chin_dx, chin)]
    return SH.spline(pts)


def face_outline(s: FaceSpec):
    """Egg-oval head (hairline to chin). Frontal: one half mirrored. 3/4:
    the near half is 8 % wider, the far half 22 % narrower and the chin
    swings toward the turn, so the features' 12 % shift sits inside it."""
    import shapely
    from shapely.geometry import Polygon
    if s.turn == 0:
        return SH.bilateral_poly(_half(s.cx, s.top, s.chin, s.half_w, -1), s.cx)
    t = float(np.sign(s.turn))
    near = _half(s.cx, s.top, s.chin, s.half_w * 1.08, -t, chin_dx=t * 0.10 * s.half_w)
    far = _half(s.cx, s.top, s.chin, s.half_w * 0.90, t, chin_dx=t * 0.10 * s.half_w)
    ring = np.vstack([near, far[::-1][1:-1]])
    g = Polygon(ring)
    return g if g.is_valid else shapely.make_valid(g)


def _eye(ex, ey, w, rise, dip, tilt, flip):
    """Upper / lower lid centrelines for one eye (flip: outer corner on +x)."""
    xi, xo = (ex - w / 2, ex + w / 2) if flip else (ex + w / 2, ex - w / 2)
    yi, yo = ey, ey - tilt
    # upper lid: arc peaking a little toward the outer corner (heavy lid)
    up = SH.spline([(xo, yo), (ex + (xo - ex) * 0.25, ey - rise), (ex + (xi - ex) * 0.55, ey - rise * 0.8), (xi, yi)])
    lo = SH.spline([(xo, yo), (ex + (xo - ex) * 0.1, ey + dip), (xi, yi)])
    return up, lo


def face_features(s: FaceSpec) -> Frag:
    f = Frag()
    cx = s.cx + 0.12 * 2 * s.half_w * s.turn         # features shift 12 % of the width toward the turn
    ey = s.eye_y
    for side in (-1, 1):                                # -1 viewer's left eye
        far = s.turn != 0 and np.sign(side) != np.sign(s.turn)
        k = 0.7 if far else 1.0
        w = s.eye_w * k
        ex = cx + side * s.eye_dx * (0.68 if far else 1.0)
        flip = side > 0
        up, lo = _eye(ex, ey, w, s.lid_rise, s.lid_dip, s.tilt, flip)
        f += MC.stroke(up, T.RULE)
        f += MC.stroke(lo, T.FINE)
        f += MC.dot(ex, ey - s.pupil_up, s.pupil_d)
        if s.crease:
            cr = SH.spline([(ex - side * w * 0.40, ey - s.lid_rise - s.crease_gap + 1.2),
                            (ex + side * w * 0.05, ey - s.lid_rise - s.crease_gap - 0.6),
                            (ex + side * w * 0.46, ey - s.lid_rise - s.crease_gap + 2.4)])
            f += MC.stroke(cr, T.FINE)
        # brow
        by = ey - s.lid_rise - (s.crease_gap if s.crease else 0) - s.brow_gap
        xin = ex - side * (w / 2 + s.brow_in)
        xout = ex + side * (w / 2 + s.brow_out * (0.2 if far else 1.0))
        brow = SH.spline([(xin, by + s.brow_slope), (ex + side * w * 0.05, by - s.brow_rise),
                          (xout, by + s.brow_rise * 0.55)])
        f += MC.stroke(brow, T.MEDIUM)
    # nose
    by0 = ey - s.lid_rise - (s.crease_gap if s.crease else 0) - s.brow_gap
    ntop = s.nose_top if s.nose_top is not None else by0 + 5.0
    nb = ey + s.nose_len
    if s.turn == 0:
        for side in (-1, 1):
            x = cx + side * s.bridge
            f += MC.stroke(_hook_ridge(x, ntop, nb, side, s.hook_r), T.MEDIUM)
        tip = SH.spline([(cx - s.tip_w, nb + 1.6), (cx, nb + 3.0), (cx + s.tip_w, nb + 1.6)])
        f += MC.stroke(tip, T.MEDIUM)
    else:
        t = float(np.sign(s.turn))                      # the nose points toward the turn:
        x = cx + t * s.bridge                           # one ridge on that (far) side,
        f += MC.stroke(_hook_ridge(x, ntop, nb, -t, s.hook_r), T.MEDIUM)   # hook curling to the near side
        tip = SH.spline([(x, nb + 1.0), (x - t * s.tip_w * 0.9, nb + 3.0), (x - t * s.tip_w * 1.8, nb + 1.4)])
        f += MC.stroke(tip, T.MEDIUM)
    # mouth
    my, mw, b = s.mouth_y, s.mouth_w, s.bow
    kl = 0.72 if s.turn < 0 else 1.0                # far half of the mouth foreshortened
    kr = 0.72 if s.turn > 0 else 1.0
    bowp = SH.spline([(cx - mw * kl, my + 1.8), (cx - mw * 0.45 * kl, my - b * 0.35), (cx, my + b * 0.45),
                      (cx + mw * 0.45 * kr, my - b * 0.35), (cx + mw * kr, my + 1.8)])
    f += MC.stroke(bowp, T.MEDIUM)
    ll = SH.spline([(cx - s.lower_w, my + s.lower_lip - 0.6), (cx, my + s.lower_lip + 1.0),
                    (cx + s.lower_w, my + s.lower_lip - 0.6)])
    f += MC.stroke(ll, T.FINE)
    if s.ear:
        for side in (-1, 1):
            if s.turn != 0 and np.sign(side) != np.sign(-s.turn):
                continue
            x = s.cx + side * (s.half_w - 1)
            c = SH.spline([(x, s.ear_y - s.ear_h / 2), (x + side * 9, s.ear_y - s.ear_h * 0.25),
                           (x + side * 8, s.ear_y + s.ear_h * 0.2), (x + side * 1, s.ear_y + s.ear_h / 2)])
            f += MC.stroke(c, T.MEDIUM)
    return f


def _hook_ridge(x, y0, y1, side, r):
    """Straight ridge x from y0 down to y1 - r, then a hook turning OUTWARD
    (toward ``side``) and back up: the alar wing."""
    ridge = SH.seg((x, y0), (x, y1 - r * 0.2))
    # hook: circle of radius r centred outward of the ridge end
    c = (x + side * r, y1 - r * 0.2)
    a0 = 180 if side > 0 else 0
    sweep = -200 if side > 0 else 200     # down and round, ending pointing up
    hook = SH.arc(c[0], c[1], r, a0, a0 + sweep, n=28)
    return np.vstack([ridge, hook[1:]])
