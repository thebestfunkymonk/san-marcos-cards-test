"""Court face kit (brief §H.0) — one hand for all twelve faces.

Kit, at final size:
  head   egg-oval ≈ 88–96 × 112–116 (wider at the temples than the jaw)
  eyes   vesica 24 × 10, Ø6 pupil dot; upper lid RULE (4.2), lower lid FINE
  brow   one MEDIUM arc
  nose   MEDIUM: a straight ridge ending in a small hook (the nostril wing)
  mouth  MEDIUM two-arc upper-lip bow + FINE lower-lip tick
  ear    a C (MEDIUM), only when hair leaves it visible
  ≤ 14 strokes; skin is paper, never hatched.

Frontal faces are authored as the LEFT half and mirrored (perfect bilateral
symmetry). 3/4 faces shift the features 12 % of the face width toward the
turn and draw the far eye at 70 % width; the nose becomes one ridge on the
far side of the axis with its hook toward the near cheek. Profiles show one
eye (see ``profile_face``).

Every function returns a ``Face``: the head silhouette (FILL d), the feature
lines (a Frag, ink), a stroke count, and named anchors (px) that the hair,
beard and crown builders use so all courts stay in register.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from deck import tokens as T
from deck.motifs import core as MC
from inkkit import geom as G

from bez import K, path, sym, mirror, open_sym


@dataclass
class Face:
    sil: str
    lines: MC.Frag
    strokes: int
    anchors: dict = field(default_factory=dict)


@dataclass
class FaceSpec:
    """Proportions, as offsets from (cx, eye line). Defaults = the K♠ king."""
    w: float = 94.0          # head width at the temples
    top: float = -44.0       # head top (under the crown)
    chin: float = 72.0       # chin
    jaw_w: float = 78.0      # width at the jaw corner
    eye_dx: float = 22.5     # eye centre from the axis
    eye_w: float = 24.0
    eye_up: float = 2.9      # upper-lid sagitta (smaller = heavier lid)
    eye_lo: float = 3.9      # lower-lid sagitta
    droop: float = 1.2       # outer corner lower than inner (calm, weighty)
    flick: float = 3.2       # upper lid runs this far past the outer corner (0 = none)
    pupil_dy: float = 1.3    # + = pupil lower; the lid covers its top (heavy-lidded)
    brow_y: float = -11.5    # brow height at its middle
    brow_arch: float = 2.6   # brow sagitta
    brow_in: float = 9.0     # inner end, from the axis
    brow_out: float = 38.0   # outer end, from the axis
    nose_top: float = 8.0    # ridge start (below the eye line)
    nose_base: float = 38.0  # nostril bottom
    nose_dx: float = 7.2     # ridge offset from the axis at the nostrils
    bridge_dx: float = 4.6   # ridge offset at the top (a narrow bridge)
    mouth_y: float = 58.0
    mouth_w: float = 13.0    # half-width
    lip_y: float = 66.0
    lip_w: float = 6.0       # half-width of the lower-lip tick
    ears: bool = False


def _eye(ex, ey, s: FaceSpec, width=None, side=-1):
    """One eye centred at (ex, ey). side −1 = viewer's left eye (outer corner
    to the left)."""
    w = s.eye_w if width is None else width
    o = (ex + side * w / 2, ey + s.droop)          # outer corner
    i = (ex - side * w / 2, ey)                    # inner corner
    # upper lid: outer → inner, bowing up (sagitta eye_up, peak nearer the inner third)
    th_u = math.degrees(2 * math.atan2(2 * s.eye_up, w))
    dirn = 0 if side < 0 else 180
    # the upper lid runs a short flick past the outer corner (a drawn eye,
    # not a stencil): o2 is 3.2 px beyond and 0.9 px below the corner
    o2 = (o[0] + side * s.flick, o[1] + 0.9)
    up = ([K(*o2, ao=dirn - side * 12, lo=1.2), K(*o, ai=dirn - side * 20, ao=dirn + side * th_u * 1.15,
                                                  li=1.0, lo=w * 0.36)] if s.flick else
          [K(*o, ao=dirn + side * th_u * 1.15, lo=w * 0.36)]) + \
         [K(*i, ai=dirn - side * th_u * 0.85, li=w * 0.30)]
    th_l = math.degrees(2 * math.atan2(2 * s.eye_lo, w))
    lo = [K(*o, ao=dirn - side * th_l, lo=w * 0.33), K(*i, ai=dirn + side * th_l, li=w * 0.33)]
    f = MC.stroke(path(up), T.RULE, role="lid")
    f += MC.stroke(path(lo), T.FINE, role="lid-lo")
    f += MC.dot(ex, ey + s.pupil_dy - 0.3, 6.0, role="pupil")
    return f


def frontal_face(cx: float, ey: float, s: FaceSpec | None = None) -> Face:
    s = s or FaceSpec()
    hw = s.w / 2
    sil = sym([K(cx, ey + s.top, 180),
               K(cx - hw * 0.86, ey + s.top + 16, 128),
               K(cx - hw, ey + 8, 92),
               K(cx - s.jaw_w / 2, ey + s.chin - 26, 62),
               K(cx, ey + s.chin, 0, li=s.jaw_w * 0.30)], cx)
    f = MC.Frag()
    # --- LEFT half (mirrored below) -------------------------------------
    half = MC.Frag()
    half += _eye(cx - s.eye_dx, ey, s)
    # brow: one arc, inner end a touch lower than the outer (level, calm)
    b0 = (cx - s.brow_in, ey + s.brow_y + 2.6)
    bm = (cx - (s.brow_in + s.brow_out) * 0.45, ey + s.brow_y - 0.6)
    b1 = (cx - s.brow_out, ey + s.brow_y + 2.2)
    half += MC.stroke(path([K(*b0, ao=196, lo=5), K(*bm, 181, li=6, lo=6), K(*b1, ai=160, li=6)]),
                      T.MEDIUM, role="brow")
    # nose: straight ridge, then the hook curls out and back under (nostril wing)
    n0 = (cx - s.bridge_dx, ey + s.nose_top)
    n1 = (cx - s.nose_dx - 1.2, ey + s.nose_base - 8)
    nose = [K(*n0, ao=96), K(*n1, ai=97, ao=100, li=6, lo=3),
            K(cx - s.nose_dx - 4.6, ey + s.nose_base - 3.5, 92, li=3, lo=2.5),
            K(cx - s.nose_dx - 1.0, ey + s.nose_base, 8, li=2.5, lo=3),
            K(cx - 4.0, ey + s.nose_base - 1.6, -30, li=2.5)]
    half += MC.stroke(path(nose), T.MEDIUM, role="nose")
    f += half + half.mirror_x(cx)
    # mouth: two-arc bow (one symmetric stroke) + lower-lip tick
    m = open_sym([K(cx - s.mouth_w, ey + s.mouth_y + 1.5, ao=-16, lo=5),
                   K(cx, ey + s.mouth_y + 0.8, ai=18, li=5)], cx)
    f += MC.stroke(m, T.MEDIUM, role="mouth")
    f += MC.stroke(open_sym([K(cx - s.lip_w, ey + s.lip_y - 0.8, ao=12), K(cx, ey + s.lip_y + 0.4, 0)], cx),
                   T.FINE, role="lip")
    strokes = 2 * (4 + 1) + 2 + 1                       # eyes(3)+brow+nose per side, mouth, lip, contour
    anchors = dict(cx=cx, ey=ey, top=ey + s.top, chin=ey + s.chin, temple=(cx - hw, ey + 8),
                   jaw=(cx - s.jaw_w / 2, ey + s.chin - 26), mouth=(cx, ey + s.mouth_y),
                   nose_base=(cx, ey + s.nose_base), brow=ey + s.brow_y, w=s.w)
    return Face(sil, f, strokes, anchors)


def three_quarter_face(cx: float, ey: float, turn: int = -1, s: FaceSpec | None = None) -> Face:
    """3/4 face turned toward ``turn`` (−1 = viewer's left, +1 = right).
    Features shift 12 % of the width toward the turn; the far eye is 70 %
    wide; one nose ridge on the far side of the feature axis, hook toward the
    near cheek; the far cheek is flatter, the near jaw rounder."""
    s = s or FaceSpec()
    hw = s.w / 2
    fx = cx + turn * 0.12 * s.w                        # feature axis
    near, far = -turn, turn                             # near side is opposite the turn
    sil = path([K(cx, ey + s.top, 180),
                K(cx - hw * 0.9, ey + s.top + 18, 118),
                K(cx - hw, ey + 10, 90 + turn * 4),
                K(cx - s.jaw_w / 2 + (6 if turn < 0 else -2), ey + s.chin - 24, 60 + turn * 8),
                K(fx + turn * 6, ey + s.chin, 0 if turn > 0 else 0, li=16, lo=16),
                K(cx + s.jaw_w / 2 + (2 if turn > 0 else -6), ey + s.chin - 24, -60 + turn * 8),
                K(cx + hw, ey + 10, -90 + turn * 4),
                K(cx + hw * 0.9, ey + s.top + 18, -118)], closed=True)
    f = MC.Frag()
    for side in (-1, 1):
        is_far = side == turn
        w = s.eye_w * (0.7 if is_far else 1.0)
        ex = fx + side * s.eye_dx * (0.8 if is_far else 1.0)
        f += _eye(ex, ey, s, width=w, side=side)
        bi, bo = s.brow_in * (0.8 if is_far else 1.0), s.brow_out * (0.78 if is_far else 1.0)
        b0 = (fx + side * bi, ey + s.brow_y + 2)
        b1 = (fx + side * bo, ey + s.brow_y + 0.5)
        f += MC.stroke(path([K(*b0, ao=190 if side < 0 else -10, lo=8),
                             K(*b1, ai=165 if side < 0 else 15, li=7)]), T.MEDIUM, role="brow")
    # nose on the far side of the axis, hook toward the near cheek
    nx = fx + turn * 3
    nose = [K(nx, ey + s.nose_top - 6, ao=90), K(nx + turn * 5, ey + s.nose_base - 8, ai=80 + turn * -8, li=10),
            K(nx + turn * 3, ey + s.nose_base, ai=110 if turn > 0 else 70, ao=180 if turn > 0 else 0, li=4, lo=4),
            K(nx - turn * 7, ey + s.nose_base - 3, ai=-150 if turn > 0 else -30, li=4)]
    f += MC.stroke(path(nose), T.MEDIUM, role="nose")
    m0, m1 = fx - s.mouth_w * (0.8 if turn < 0 else 1.0), fx + s.mouth_w * (0.8 if turn > 0 else 1.0)
    f += MC.stroke(path([K(m0, ey + s.mouth_y + 1, ao=-6), K(fx, ey + s.mouth_y - 0.8, ai=12, ao=-12, li=3, lo=3),
                         K(m1, ey + s.mouth_y + 1, ai=6)]), T.MEDIUM, role="mouth")
    f += MC.stroke(path([K(fx - s.lip_w, ey + s.lip_y - 0.8, ao=12), K(fx + s.lip_w, ey + s.lip_y - 0.8, ai=-12)]),
                   T.FINE, role="lip")
    anchors = dict(cx=cx, fx=fx, ey=ey, top=ey + s.top, chin=ey + s.chin, turn=turn)
    return Face(sil, f, 12, anchors)


def profile_face(cx: float, ey: float, facing: int = -1, s: FaceSpec | None = None) -> Face:
    """Strict profile facing ``facing`` (−1 = viewer's left). One eye (a
    half-vesica open toward the face front), brow, nose as the silhouette's own
    ridge and hook, mouth tick, ear C. The silhouette carries the nose.
    Facing right is the exact mirror of facing left (one drawing, two ways)."""
    s = s or FaceSpec()
    if facing > 0:
        fl = profile_face(cx, ey, -1, s)
        a = dict(fl.anchors, facing=+1, front=2 * cx - fl.anchors["front"])
        return Face(G.mirror_x(fl.sil, cx), fl.lines.mirror_x(cx), fl.strokes, a)
    d = -1
    hx = cx - d * 6                                   # skull centre behind the face
    fr = cx + d * s.w * 0.46                          # face front line
    sil = path([K(hx, ey + s.top, 180 if d < 0 else 0),
                K(fr - d * 10, ey - 30, 90 + d * -40),
                K(fr, ey - 8, 90),                    # brow ridge
                K(fr - d * 3, ey + 2, 90),            # nose root
                K(fr + d * 14, ey + s.nose_base - 4, ai=90 + d * -38, ao=90 + d * 60, li=10, lo=4),  # nose tip
                K(fr + d * 2, ey + s.nose_base + 2, ai=180 if d < 0 else 0, ao=90),
                K(fr + d * 1, ey + s.mouth_y, 90),
                K(fr - d * 1, ey + s.chin - 4, ai=90, ao=180 if d > 0 else 0),
                K(hx - d * 10, ey + s.chin + 2, 180 if d > 0 else 0),
                K(hx - d * s.w * 0.52, ey + 20, -90),
                K(hx - d * s.w * 0.40, ey + s.top + 14, -90 + d * 40)], closed=True)
    ex = fr - d * 17
    f = MC.stroke(path([K(ex - d * 9, ey + 1, ao=-20 if d > 0 else 200), K(ex + d * 5, ey - 1.5, ai=10 if d > 0 else 170)]),
                  T.RULE, role="lid")
    f += MC.stroke(path([K(ex - d * 7, ey + 2, ao=25 if d > 0 else 155), K(ex + d * 4, ey + 4.5, ai=-15 if d > 0 else 195)]),
                   T.FINE, role="lid-lo")
    f += MC.dot(ex + d * 1, ey + 0.8, 6.0, role="pupil")
    f += MC.stroke(path([K(ex - d * 10, ey + s.brow_y + 1, ao=-10 if d > 0 else 190), K(fr - d * 4, ey + s.brow_y + 3, ai=15 if d > 0 else 165)]),
                   T.MEDIUM, role="brow")
    f += MC.stroke(path([K(fr - d * 10, ey + s.nose_base - 4, ao=90 + d * 50), K(fr - d * 4, ey + s.nose_base + 1, ai=d * 10 if d > 0 else 180 + 10)]),
                   T.MEDIUM, role="nostril")
    f += MC.stroke(path([K(fr - d * 1, ey + s.mouth_y, ao=180 if d > 0 else 0), K(fr - d * 12, ey + s.mouth_y + 2, ai=170 if d > 0 else 10)]),
                   T.MEDIUM, role="mouth")
    ear_x = hx - d * 18
    f += MC.stroke(path([K(ear_x + d * 2, ey - 4, ao=180 if d > 0 else 0), K(ear_x - d * 8, ey + 10, 90),
                         K(ear_x + d * 1, ey + 26, ai=0 if d > 0 else 180)]), T.MEDIUM, role="ear")
    return Face(sil, f, 8, dict(cx=cx, ey=ey, front=fr, facing=d, top=ey + s.top, chin=ey + s.chin))
