"""art/_qh_face.py — the Q♥ face: the §H.0 face kit, 3/4 right, feminine.

Built on deck.courtkit's 3/4 construction (the turned Moss egg, the 12 %
feature shift, the far eye at 70 % joining the contour, the far pupil
centred) with four queen-specific marks that the kit does not offer:

* WINGED upper lids — the RULE lid runs past the outer corner and lifts a
  few px (the mid-century eyeliner flick). Still one RULE stroke per lid.
* ARCHED brows — one MEDIUM arc each, peaked two-thirds of the way out
  (two tangent arcs in one stroke), higher above the half-lidded eye.
* a DELICATE nose — the straight MEDIUM ridge plus a small rounded hook
  (the nostril) instead of the kit's long level foot.
* a CUPID'S-BOW mouth with a faint smile — the two-arc upper-lip bow whose
  corners lift, and a fuller FINE lower-lip arc.

§H.0 limits hold: ≤ 14 strokes (this face: 11), paper skin, 24 × 10 eye
vesicas with Ø6 pupils (RULE upper lid, FINE lower lid), one brow arc per
eye, straight ridge + small hook, two-arc bow + FINE lower-lip tick.

Upstream candidates: FaceSpec.wing (a lifted flick), FaceSpec.brow_peak and
FaceSpec.nose_hook for queens (see the QH report).
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

from deck import courtkit as K
from deck.motifs import core as C

FINE, MEDIUM, RULE = K.FINE, K.MEDIUM, K.RULE
P = K.P


def _winged_eye(ex, ey, s, w, side, *, wing=(4.0, -2.2), lid_sag=None, low_sag=None, pupil=True, pdx=None,
                far=False, wing_mode="arc"):
    """One eye (side −1: outer corner on the viewer's left), a 24 × 10
    vesica. The upper lid is ONE RULE arc from the inner corner over the lid
    to the WING TIP beyond the outer corner (dx outward, dy up): the lid
    itself sweeps up into the mid-century flick, no kink. The FINE lower lid
    runs from the inner corner to the point where the upper arc crosses the
    outer corner's vertical. The Ø6 pupil hangs from the lid (kit rule)."""
    f = C.Frag()
    k = w / s.eye_w
    ls = (s.lid_sag if lid_sag is None else lid_sag) * k
    lo = (s.low_sag if low_sag is None else low_sag) * k
    inner = P(ex - side * w / 2, ey)
    outer = P(ex + side * w / 2, ey)
    if wing is None or far:
        f += K.line(K.arc_sag(inner, outer, side * ls), RULE, role="lid")
        f += K.line(K.arc_sag(inner, outer, -side * lo), FINE, role="lid-lo")
    elif wing_mode == "hook":
        # the vesica lid, then a short reverse-curving flick: the lid's own
        # tangent at the outer corner (down and out) turns UP on a small arc
        up = K.arc_sag(inner, outer, side * ls)
        pts = C.sample_d(up, 0.2)[0][0]
        t_ = pts[-1] - pts[-3]
        h = math.degrees(math.atan2(t_[1], t_[0]))
        tu = C.Turtle(outer[0], outer[1], h)
        tu.arc(wing[0], -side * wing[1])       # turn UP, away from the lower lid
        tu.fd(wing[2] if len(wing) > 2 else 0.0)
        f += K.line(up + tu.d().replace("M", "L", 1), RULE, role="lid")
        f += K.line(K.arc_sag(inner, outer, -side * lo), FINE, role="lid-lo")
    else:
        apex = P(ex + side * 1.0, ey - ls)
        tip = outer + P(side * wing[0], wing[1])
        f += K.line(K.arc3(inner, apex, tip), RULE, role="lid")
        # where the upper arc crosses x = outer: the lower lid's outer end
        c, r = K.circ3(inner, apex, tip)
        dy_ = math.sqrt(max(r * r - (outer[0] - c[0]) ** 2, 0.0))
        yo = min((c[1] + dy_, c[1] - dy_), key=lambda v: abs(v - ey))
        o2 = P(outer[0], yo)
        f += K.line(K.arc_sag(inner, o2, -side * lo), FINE, role="lid-lo")
    if pupil:
        f += _pupil(f, ex + (s.pupil_dx * k if pdx is None else pdx))
    return f


def _y_at(frag, role, x, pick):
    """y of the centreline of the stroke with ``role`` at abscissa x
    (``pick`` min → the upper crossing, max → the lower)."""
    ys = []
    for m in frag.marks:
        if m.role != role:
            continue
        for pts, _ in K.G.flatten(m.d, 0.05):
            for a, b in zip(pts[:-1], pts[1:]):
                if (a[0] - x) * (b[0] - x) <= 0 and a[0] != b[0]:
                    t = (x - a[0]) / (b[0] - a[0])
                    ys.append(a[1] + t * (b[1] - a[1]))
    return pick(ys) if ys else None


def _pupil(eye, px, d=6.0):
    """The Ø6 pupil between the lids at x = px: if the paper between the
    RULE lid and the FINE lower lid is ≤ 6.4 px tall the pupil touches both
    (the half-lidded gaze); otherwise it hangs from the upper lid, and the
    lower gap is either ≥ 3 px or closed (§I.12)."""
    yu = _y_at(eye, "lid", px, min)
    yl = _y_at(eye, "lid-lo", px, max)
    top, bot = yu + RULE / 2, yl - FINE / 2
    if bot - top <= d + 0.4:
        cy = (top + bot) / 2
    else:
        cy = top + d / 2 - 0.6
        if 0 < bot - (cy + d / 2) < K.GAP_MARK:
            cy = bot - d / 2 + 0.4
    return K.dot((px, cy), d, role="pupil")


def _arched_brow(p_in, p_out, peak_t=0.62, rise=4.2):
    """A brow as ONE MEDIUM stroke of two tangent arcs through the inner end,
    a peak (``peak_t`` of the way out, ``rise`` px above the chord) and the
    outer end — the arched mid-century brow."""
    p_in, p_out = P(p_in), P(p_out)
    pk = p_in + (p_out - p_in) * peak_t + P(0.0, -rise)
    d, _, _ = K.FM.arc_spline([p_in, pk, p_out])
    return K.line(d, MEDIUM, role="brow")


def _nose(ax, ey, s, turn, top_dy=-2.0, bot_dy=None, tip_dx=7.0, hook_r=3.6, foot=2.4):
    """3/4 nose: the straight MEDIUM ridge from under the far brow's inner end
    down toward the turn, then a small hook round the tip back toward the
    near cheek (the nostril) — short, so it reads delicate."""
    bot = s.nose_bot_dy if bot_dy is None else bot_dy
    p0 = P(ax + turn * 2.0, ey + top_dy)
    p1 = P(ax + turn * tip_dx, ey + bot - 4.5)
    h = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    t = C.Turtle(p0[0], p0[1], h)
    t.line_to(p1[0], p1[1])
    target = 180.0 if turn > 0 else 0.0
    sweep = ((target - t.heading + 540) % 360) - 180
    t.arc(hook_r, sweep)
    if foot:
        t.fd(foot)
    return K.line(t.d(), MEDIUM, role="nose")


def _mouth(fx, y, hw_l, hw_r, *, rise=1.8, lift=1.0, sag=-1.0, lip_dy=7.8, lip_hw=5.6, lip_sag=-2.4):
    """Cupid's bow: two arcs from the corners (lifted ``lift`` px: the faint
    smile) up to the centre cusp (``rise`` above the corners' mean); a FINE
    lower-lip arc below it."""
    f = C.Frag()
    lc, rc = P(fx - hw_l, y - lift), P(fx + hw_r, y - lift)
    cusp = P(fx, y - rise)
    # each half dips a little (a bow) between its corner and the cusp
    d = K.arc_sag(lc, cusp, sag) + K.arc_sag(cusp, rc, sag, move=False)
    f += K.line(d, MEDIUM, role="mouth")
    kl, kr = lip_hw * hw_l / max(hw_l, hw_r), lip_hw * hw_r / max(hw_l, hw_r)
    ly = y + lip_dy
    f += K.line(K.arc_sag(P(fx - kl, ly), P(fx + kr, ly), lip_sag), FINE, role="lip")
    return f


def queen_face(center, turn=+1, *, eye_w=24.0, lid_sag=3.0, low_sag=6.2, wing=(4.2, -2.4), wing_mode="arc",
               brow_rise=4.6,
               brow_dy=-15.5, nose_bot=16.5, mouth_dy=37.5, lip_dy=7.6, mouth_hw=8.6, smile=1.3, spec_over=None):
    """The Q♥ face, 3/4 toward ``turn`` (+1 = viewer's right). Returns a
    courtkit Face (head d, skin region, lines, anchors, strokes)."""
    s = K.FaceSpec()
    for k_, v in K.SEX_PRESETS["f"].items():
        setattr(s, k_, v)
    for k_, v in K.LID_PRESETS["half"].items():
        setattr(s, k_, v)
    s.eye_w = eye_w
    s.lid_sag, s.low_sag = lid_sag, low_sag
    s.mouth_dy, s.mouth_hw = mouth_dy, mouth_hw
    s.lip_dy = mouth_dy + lip_dy
    s.nose_bot_dy = nose_bot
    s.brow_dy = brow_dy
    for k_, v in (spec_over or {}).items():
        setattr(s, k_, v)
    cx, cy = float(center[0]), float(center[1])
    ey = cy + s.eye_dy
    shift = turn * s.turn_shift * 2 * s.r
    ax = cx + shift
    s.pupil_dx = turn * 2.0
    head, info = K.egg((cx, cy), s.r, chin_dx=shift * s.chin_swing)
    near, far = -turn, turn
    lines = C.Frag()
    # near eye: full width, winged
    ne_x = ax + near * s.eye_dx
    lines += _winged_eye(ne_x, ey, s, s.eye_w, near, wing=wing, wing_mode=wing_mode)
    # far eye: 70 % wide, its outer corner joining the head contour (kit rule)
    fe_w = s.eye_w * s.far_eye
    cx_far = K._side_x(info, cx, cy, s.r, ey, far)
    fe_x = cx_far - far * (0.8 + fe_w / 2)
    lines += _winged_eye(fe_x, ey, s, fe_w, far, wing=None, pdx=-far * 0.6, far=True)
    # brows: arched; the near one full, the far one ending on the contour
    b_in = P(ax + near * s.brow_in, ey + s.brow_dy)
    b_out = P(ax + near * (s.brow_out + 1.0), ey + s.brow_dy + s.brow_drop + 1.0)
    lines += _arched_brow(b_in, b_out, peak_t=0.58, rise=brow_rise)
    by = ey + s.brow_dy + s.brow_drop * 0.6 + 0.5
    fb_out = P(K._side_x(info, cx, cy, s.r, by, far) - far * 0.8, by)
    fb_in = P(ax + far * s.brow_in * 0.8, ey + s.brow_dy)
    lines += _arched_brow(fb_in, fb_out, peak_t=0.45, rise=brow_rise * 0.8)
    lines += _nose(ax, ey, s, turn)
    hw_far = s.mouth_hw * 0.78
    hl, hr = (hw_far, s.mouth_hw) if turn < 0 else (s.mouth_hw, hw_far)
    lines += _mouth(ax + turn * 1.5, ey + s.mouth_dy, hl, hr, lift=smile, lip_dy=lip_dy)
    skin = K.R(head)
    anchors = K._anchors(cx, cy, s, info, ax, ey, turn, 0)
    return K.Face(head, skin, lines, anchors, K._count(lines))
