"""art/_jc_face.py — J♣'s 3/4-left face: the §H.0 face kit, adapted.

courtkit.face('3/4-left') joins the far eye's outer corner to the head
contour and centres its pupil; with the jack's gaze thrown LEFT (downstream)
the near pupil looks left while the far one looks at the viewer, and the
squeezed far eye reads as a squint. Here the far eye is a whole 70 % almond
standing free inside the far cheek (3 px + the contour's half-width clear of
it), both pupils look the same way, and the nose is the kit's straight ridge
with a hook set so it clears the far eye's inner corner. Everything else is
the kit: the egg (with the 3/4 chin swing), 24 × 10 vesica eyes with RULE
upper and FINE lower lids, Ø6 pupils hanging from the lids, MEDIUM brow arcs,
the two-arc lip bow and the FINE lower-lip tick; ≤ 14 strokes.

Upstream candidate: courtkit.face(..., far_eye_free=True, far_pupil_dx=…).
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

from deck import courtkit as K
from deck.motifs import core as C

P = K.P
MEDIUM, FINE, RULE, CONTOUR = K.MEDIUM, K.FINE, K.RULE, K.CONTOUR


def face34(center=(385.0, 207.0), *, age="young", lids="level", far_edge=CONTOUR, far_gap=3.4,
           near_pdx=-2.6, far_pdx=-1.0, nose_top=(-0.5, -2.5), nose_tip=(-7.5, 15.5), hook=(3.6, 3.0),
           wing=(3.4, -120.0),
           far_brow_end=2.0, near_brow=None, far_brow_sag=2.4, mouth_dx=-1.5, chin_r=None, chin_dy=None,
           **over) -> K.Face:
    """A 3/4-LEFT face (turned toward the viewer's left).

    far_edge   the stroke that will run along the far cheek at the eye line
               (CONTOUR where the cheek meets paper, MEDIUM against hair);
    far_gap    paper between that stroke and the far eye's outer corner;
    near_pdx / far_pdx   pupil offsets (negative: looking left);
    nose_top / nose_tip  the ridge's ends, (dx from the feature axis, dy from
               the eye line); ``hook`` = (radius, run) of the tip and nose base;
               ``wing`` = (radius, sweep) of the alar curl (None: none);
    near_brow  optional dict of FaceSpec brow overrides for the near brow;
    chin_r / chin_dy  the egg's chin circle (a broader chin reads younger-male).
    Keyword overrides go to the FaceSpec (as courtkit.face)."""
    s = K.FaceSpec()
    for k, v in K.AGE_PRESETS.get(age, {}).items():
        setattr(s, k, getattr(s, k) + v)
    for k, v in K.LID_PRESETS.get(lids, {}).items():
        setattr(s, k, v)
    for k, v in over.items():
        if not hasattr(s, k):
            raise TypeError(f"face34(): unknown FaceSpec field {k!r}")
        setattr(s, k, v)
    cx, cy = float(center[0]), float(center[1])
    turn = -1
    shift = turn * s.turn_shift * 2 * s.r
    ax = cx + shift
    ey = cy + s.eye_dy
    head, info = K.egg((cx, cy), s.r, chin_dx=shift * s.chin_swing, chin_r=chin_r, chin_dy=chin_dy)
    lines = C.Frag()
    near, far = +1, -1
    # near eye: the full 24 × 10 vesica
    lines += K._eye(ax + near * s.eye_dx, ey, s, s.eye_w, near, lids, False, pdx=near_pdx)
    # far eye: 70 % wide, free inside the far cheek
    fe_w = s.eye_w * s.far_eye
    x_cheek = K._side_x(info, cx, cy, s.r, ey, far)
    fe_x = x_cheek - far * (far_edge / 2 + far_gap + RULE / 2 + fe_w / 2)
    lines += K._eye(fe_x, ey, s, fe_w, far, lids, False, pdx=far_pdx)
    # brows: the near one the kit's; the far one shortened, ending short of the contour
    sb = replace(s, **(near_brow or {}))
    lines += K._brow(ax, sb, near, ey)
    by = ey + s.brow_dy + s.brow_drop * 0.6
    xo = K._side_x(info, cx, cy, s.r, by, far) - far * (far_edge / 2 + far_brow_end + MEDIUM / 2)
    b_out = P(xo, by)
    b_in = P(ax + far * s.brow_in * 0.75, ey + s.brow_dy)
    lines += K.line(K.arc_sag(b_out, b_in, far_brow_sag), MEDIUM, role="brow")
    # nose: one straight ridge down toward the turn, then the nostril hook back
    p0 = P(ax + nose_top[0], ey + nose_top[1])
    p1 = P(ax + nose_tip[0], ey + nose_tip[1])
    h = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    t = C.Turtle(p0[0], p0[1], h)
    t.line_to(p1[0], p1[1])
    sweep = ((0.0 - t.heading + 540) % 360) - 180
    t.arc(hook[0], sweep)
    t.fd(hook[1])
    if wing:
        t.arc(wing[0], wing[1])           # the alar wing curling up on the near side
    lines += K.line(t.d(), MEDIUM, role="nose")
    hw_far = s.mouth_hw * 0.78
    lines += K._mouth(ax + mouth_dx, s, ey, hw_far, s.mouth_hw)
    skin = K.R(head)
    anchors = K._anchors(cx, cy, s, info, ax, ey, turn, 0)
    anchors["far_eye_x"] = fe_x
    return K.Face(head, skin, lines, anchors, K._count(lines))


# ---------------------------------------------------------------------------
# face_jc: the J♣ head, a drawn 3/4 contour (not a turned egg)
# ---------------------------------------------------------------------------
from deck.motifs import forms as FM  # noqa: E402

# the 3/4-left head contour, clockwise from the crown: (point, heading).
# Skull as the kit egg's circle (r 44 about (385, 207)); the NEAR side
# (viewer's right) falls from the temple to a rounded jaw angle, the jaw
# runs down and forward to a firm, slightly squared chin swung 10 px toward
# the turn; the FAR side is flatter and rises from the chin past the cheek
# to the temple — the head turns, the features do not just slide.
JC_CONTOUR = [
    ((385.0, 163.0), 0.0),
    ((429.0, 207.0), 90.0),
    ((426.0, 238.0), 100.0),
    ((414.0, 263.0), 128.0),
    ((392.0, 281.0), 158.0),
    ((374.0, 286.0), 180.0),
    ((360.0, 281.0), 222.0),
    ((349.0, 263.0), 250.0),
    ((344.0, 238.0), 265.0),
    ((342.0, 207.0), 270.0),
    ((353.0, 177.0), 300.0),
]


JC_LOWER = [(429.0, 207.0), (426.0, 236.0), (414.0, 259.0), (395.0, 274.0), (376.0, 279.0),
            (361.0, 273.0), (350.0, 256.0), (345.0, 232.0), (341.0, 207.0)]


def contour_d(pts=JC_LOWER, dx=0.0, dy=0.0, r=44.0):
    """The head: the skull is the kit egg's circle (r about (385, 207)); the
    lower contour is ONE G1 arc spline from the near side of the circle's
    horizontal diameter, down the jaw, round the chin and up the far cheek to
    the far end of the diameter (tangent to the circle at both ends)."""
    if isinstance(pts[0][0], (tuple, list)):          # legacy (point, heading) list
        p = [P(q[0] + dx, q[1] + dy) for q, _ in pts]
        h = [hd for _, hd in pts]
        d, _ = FM.biarc_chain(p, h, closed=True)
        return d
    c = P(385.0 + dx, 207.0 + dy)
    p = [P(q[0] + dx, q[1] + dy) for q in pts]
    p[0] = P(c[0] + r, c[1])
    p[-1] = P(c[0] - r, c[1])
    lower = K.spline(p, h_start=90.0, h_end=-90.0)
    top = K.arc_c(c, r, 180.0, 360.0, move=False)
    return lower + top + "Z"


def face_jc(center=(385.0, 207.0), *, contour=JC_LOWER, lids="level", eye_dy=6.0,
            near_eye=(23.0, 24.0), far_eye=(-19.0, 17.0), near_pdx=-3.0, far_pdx=-1.6,
            near_brow=((8.0, -11.5), (36.0, -9.5), 4.2), far_brow=((-8.0, -11.5), (-27.0, -9.0), 3.2),
            nose=((-3.0, -4.0), (-11.5, 18.5), 4.0, 5.0), wing=None,
            mouth=(-2.0, 40.0, 8.0, 10.5, 1.8, -1.0), lip=(-1.0, 48.0, 5.5, -1.8),
            flick=0.0, **over) -> K.Face:
    """The J♣ 3/4-left face (§H.0 kit marks on a drawn 3/4 contour).

    Offsets are (dx, dy) from the FEATURE AXIS (the centre x shifted 12 % of
    the head width toward the turn) and the eye line (centre y + eye_dy).
    near_eye / far_eye  (dx of the eye centre, width): 24 and ~70 %;
    near_pdx / far_pdx  pupil offsets (negative: looking left, downstream);
    near_brow / far_brow  (inner end, outer end, sagitta) — MEDIUM arcs;
    nose     (ridge top, tip, hook radius, run back) — one MEDIUM ridge + hook;
    mouth    (dx, dy, far half-width, near half-width, bow rise, bow sag);
    lip      (dx, dy, half-width, sagitta) — the FINE lower-lip tick."""
    s = K.FaceSpec()
    for k, v in K.LID_PRESETS.get(lids, {}).items():
        setattr(s, k, v)
    s.flick = flick
    for k, v in over.items():
        if not hasattr(s, k):
            raise TypeError(f"face_jc(): unknown FaceSpec field {k!r}")
        setattr(s, k, v)
    cx, cy = float(center[0]), float(center[1])
    dx0, dy0 = cx - 385.0, cy - 207.0
    head = contour_d(contour, dx0, dy0)
    ax = cx - 0.12 * 2 * s.r
    ey = cy + eye_dy
    lines = C.Frag()
    ne_x, ne_w = ax + near_eye[0], near_eye[1]
    fe_x, fe_w = ax + far_eye[0], far_eye[1]
    lines += K._eye(ne_x, ey, s, ne_w, +1, lids, False, pdx=near_pdx)
    lines += K._eye(fe_x, ey, s, fe_w, -1, lids, False, pdx=far_pdx)
    for (a, b, sg) in (near_brow, far_brow):
        pa, pb = P(ax + a[0], ey + a[1]), P(ax + b[0], ey + b[1])
        p0, p1 = (pa, pb) if pa[0] < pb[0] else (pb, pa)
        lines += K.line(K.arc_sag(p0, p1, sg), MEDIUM, role="brow")
    (t0, t1, hr, run) = nose
    p0, p1 = P(ax + t0[0], ey + t0[1]), P(ax + t1[0], ey + t1[1])
    h = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    t = C.Turtle(p0[0], p0[1], h)
    t.line_to(p1[0], p1[1])
    sweep = ((0.0 - t.heading + 540) % 360) - 180
    t.arc(hr, sweep)
    t.fd(run)
    if wing:
        t.arc(wing[0], wing[1])
    lines += K.line(t.d(), MEDIUM, role="nose")
    mdx, mdy, hwl, hwr, rise, bsag = mouth
    y = ey + mdy
    mx = ax + mdx
    cusp = P(mx, y - rise)
    d = K.arc_sag(P(mx - hwl, y), cusp, bsag) + K.arc_sag(cusp, P(mx + hwr, y), bsag, move=False)
    lines += K.line(d, MEDIUM, role="mouth")
    ldx, ldy, lhw, lsag = lip
    lines += K.line(K.arc_sag(P(ax + ldx - lhw, ey + ldy), P(ax + ldx + lhw, ey + ldy), lsag), FINE, role="lip")
    skin = K.R(head)
    info = {"chin": P(374.0 + dx0, 286.0 + dy0)}

    def side_x(yy, sgn):
        g = skin.intersection(K.box(-2000, yy - 0.01, 2000, yy + 0.01))
        if g.is_empty:
            return cx + sgn * s.r
        x0, _, x1, _ = g.bounds
        return x1 if sgn > 0 else x0

    a = dict(center=P(cx, cy), axis=ax, eye_y=ey, brow_y=ey + near_brow[0][1], nose_y=ey + t1[1],
             mouth_y=y, lip_y=ey + ldy, chin=info["chin"], top=cy - s.r, r=s.r,
             temple_l=P(side_x(ey, -1), ey), temple_r=P(side_x(ey, 1), ey),
             jaw_l=P(side_x(y, -1), y), jaw_r=P(side_x(y, 1), y), crown_y=cy - s.r * 0.55,
             ear_l=P(cx - s.r + 2, ey + 12), ear_r=P(cx + s.r - 2, ey + 12), turn=-1, facing=0,
             side_x=side_x, spec=s, far_eye_x=fe_x)
    return K.Face(head, skin, lines, a, K._count(lines))
