"""art/_qs_face.py — the Q♠ face: the kit's 3/4-left queen face (deck.courtkit
.face, sex='f') with the Blind Oracle's CLOSED eyes redrawn.

The kit's closed lid is a bare RULE arc with its Ø3 dot floating ≈ 8 px below
(it reads as a mole). The oracle's eye is drawn the way the kit draws an open
one, only shut:

* the lash line: one RULE arc bulging DOWN (the upper lid lowered over the
  eye), its outer end running on into a short upturned flick (a woman's
  eye; on the far eye the outer end joins the head contour instead);
* optionally (``crease``) one FINE arc above it, following the eyeball's
  curve: the heavy, serene lid of a figure listening;
* the vestigial eye (§H.2 'a Ø3 dot beneath each lid'): the Ø3 Aquifer dot
  exactly 3 px (§I.12) under the lash line's lowest point — the blind
  salamander's eye under the skin, tucked close so it belongs to the eye.

Per eye 2–3 marks; with brows (2), nose (1) and mouth (2) the face is 9–11
strokes (§H.0 ≤ 14). Upstream: the kit's ``lids='closed'`` could take this
construction (lash arc + flick + tucked dot)."""
from __future__ import annotations

import numpy as np

from deck import courtkit as K
from deck.motifs import core as C

P = K.P


def oracle_face(center, *, lid_sag=3.6, flick=4.6, flick_deg=-28.0, crease=False, crease_sag=3.0,
                crease_gap=None, dot_gap=3.05, dot_d=3.0, dot_dx=-1.0, **over):
    fc = K.face(center, "3/4-left", sex="f", lids="closed", vestigial=True, **over)
    a = fc.anchors
    s = a["spec"]
    ey = a["eye_y"]
    ax = float(a["axis"])
    turn = a["turn"]
    near, far = -turn, turn
    keep = fc.lines.select(lambda m: m.role not in ("lid", "pupil"))
    eyes = C.Frag()
    ne_c, ne_w = P(ax + near * s.eye_dx, ey), s.eye_w
    fe_w = s.eye_w * s.far_eye
    cx_far = a["side_x"](ey, far)
    fe_c = P(cx_far - far * (0.8 + fe_w / 2), ey)
    info = {}
    for (c, w, side, is_far) in ((ne_c, ne_w, near, False), (fe_c, fe_w, far, True)):
        k = w / s.eye_w
        outer = c + P(side * w / 2, 0.0)
        inner = c - P(side * w / 2, 0.0)
        a_, b_ = (outer, inner) if side < 0 else (inner, outer)
        d = K.arc_sag(a_, b_, -lid_sag * k)
        if flick and not is_far:
            hd = flick_deg if side > 0 else 180.0 - flick_deg
            t = C.Turtle(outer[0], outer[1], hd)
            t.fd(flick)
            d = d + t.d()
        eyes += K.line(d, K.RULE, role="lid")
        low = c[1] + lid_sag * k                       # lash line's lowest point (centreline)
        if crease:
            g = crease_gap if crease_gap is not None else (K.RULE / 2 + K.GAP + K.FINE / 2 + 0.4)
            span = 0.36 if not is_far else 0.30
            ca, cb = c + P(-w * span, 0.0), c + P(w * span, 0.0)
            yy = c[1] - g + 1.2
            ca[1] = cb[1] = yy
            eyes += K.line(K.arc_sag(ca, cb, crease_sag * k), K.FINE, role="crease")
        dx = dot_dx * (1 if not is_far else 0.5) * (-turn)
        dy = low + K.RULE / 2 + dot_gap + dot_d / 2
        eyes += K.dot((c[0] + dx, dy), dot_d, role="pupil")
        info["far" if is_far else "near"] = dict(c=c, w=w, low=low)
    lines = keep + eyes
    a = dict(a)
    a["eyes"] = info
    return K.Face(fc.head, fc.skin, lines, a, K._count(lines))
