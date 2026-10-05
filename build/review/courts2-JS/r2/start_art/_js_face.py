"""art/_js_face.py — the Lantern Page's profile (§H.0 face kit, §H.3 'young
and clean-shaven, eye lifted toward the light').

The kit's profile (courtkit._profile_face) is an adult's: a long straight
nose, a notched chin and a jaw line. A page is a youth, so this is the same
construction — ONE G1 biarc chain through pinned points with pinned
tangents, built facing LEFT and mirrored for 'profile-right' — re-pinned
for youth:

* a rounder, more upright forehead and a soft brow (no brow ridge);
* a shorter nose with a slightly lifted tip (the ridge is still straight);
* fuller lips, a small soft chin, no jaw line (the hood's edge is the jaw);
* a larger eye (0.70 × 24 wide) with the RULE lid arched high — the lid
  'raised' — and the Ø6 pupil set at the FRONT of the eye, touching the lid:
  the gaze goes forward and up, to the lantern;
* a higher, arched brow.

Strokes: lid, lower lid, pupil, brow, nostril, mouth = 6 (≤ 14). The ear is
under the hood. The head region includes the neck (the hood's gorget covers it).
"""
from __future__ import annotations

import numpy as np

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM
from inkkit import geom as G

MEDIUM, FINE, RULE, CONTOUR = K.MEDIUM, K.FINE, K.RULE, K.CONTOUR


def page_profile(center, facing=+1, *, r=42.5, eye_dy=6.0, nose_len=8.0, brow_lift=0.0, eye_w=16.8,
                 lid_sag=4.6, low_sag=2.6, pupil_d=6.0, mouth_len=8.5, nostril=(7.4, 0.8, -78.0, 3.3, 160.0)):
    cx, cy = float(center[0]), float(center[1])
    if facing > 0:
        fl = page_profile(center, -1, r=r, eye_dy=eye_dy, nose_len=nose_len, brow_lift=brow_lift, eye_w=eye_w,
                          lid_sag=lid_sag, low_sag=low_sag, pupil_d=pupil_d, mouth_len=mouth_len, nostril=nostril)
        a = dict(fl.anchors)
        for k, v in list(a.items()):
            if isinstance(v, np.ndarray) and v.shape == (2,):
                a[k] = K.P(2 * cx - v[0], v[1])
        a["front"] = 2 * cx - fl.anchors["front"]
        a["axis"] = 2 * cx - fl.anchors["axis"]
        a["facing"] = +1
        hd = G.mirror_x(fl.head, cx)
        return K.Face(hd, K.R(hd), fl.lines.mirror_x(cx), a, fl.strokes)
    ey = cy + eye_dy
    fr = cx - r * 0.84                    # the face's front line (brow / lips)
    top = cy - r
    nb = ey + 17.0                        # nose base
    my = ey + 38.5                        # mouth corner line
    tip = (fr - nose_len, nb - 4.2)
    root = (fr + 3.2, ey + 0.5)
    ridge = K._hd(root, tip)
    chain_pts = [
        ((cx + 4.0, top), 180.0),                    # crown of the skull
        ((fr + 6.5, cy - 27.0), 116.0),              # a round, upright forehead
        ((fr + 0.8, ey - 9.5), 100.0),               # soft brow
        (root, ridge + 10.0),                        # a shallow nose root
        (tip, ridge - 6.0),                          # short ridge to a lifted tip
        ((fr - nose_len + 2.4, nb + 0.2), 20.0),     # round the tip, under the nose (tip lifted)
        ((fr - 0.6, nb + 2.0), 76.0),                # subnasale
        ((fr - 2.8, my - 3.8), 102.0),               # full upper lip
        ((fr + 0.2, my + 0.4), 60.0),                # mouth corner (a soft notch)
        ((fr - 1.4, my + 4.6), 112.0),               # full lower lip
        ((fr + 2.0, my + 9.6), 84.0),                # the soft hollow under the lip
        ((fr + 0.9, my + 15.5), 106.0),              # a small round chin
        ((fr + 9.0, my + 22.5), 24.0),               # under the chin
        ((fr + 19.0, my + 27.0), 64.0),              # throat
        ((fr + 22.0, my + 62.0), 88.0),              # neck front (under the hood)
        ((cx + 20.0, my + 62.0), -95.0),             # neck back
        ((cx + 23.0, ey + 32.0), -118.0),            # nape
        ((cx + r + 5.0, cy + 2.0), -88.0),           # occiput
    ]
    pts = [K.P(q) for q, _ in chain_pts]
    hs = [h for _, h in chain_pts]
    d, _ = FM.biarc_chain(pts, hs, closed=True)
    lines = C.Frag()
    # the eye: front ≥ 3 px + RULE/2 clear of the contour's inner edge at the nose root
    ex0 = fr + 3.2 + CONTOUR / 2 + K.GAP_MARK + RULE / 2 + 1.2
    front, back = K.P(ex0, ey - 0.6), K.P(ex0 + eye_w, ey + 1.0)
    lines += K.line(K.arc_sag(front, back, lid_sag), RULE, role="lid")
    lower_end = K.P(front[0] + 2.2, ey + 3.4)
    lines += K.line(K.arc_sag(lower_end, back, -low_sag), FINE, role="lid-lo")
    # the pupil at the front of the eye, hanging from the arched lid (looking forward and up)
    pu = K.P(front[0] + 4.6, ey - lid_sag * 0.62 + RULE / 2 + pupil_d / 2 - 0.4)
    lines += K.dot(pu, pupil_d, role="pupil")
    # brow: a high MEDIUM arch from over the eye's front back over the eye
    bx0 = fr + 0.8 + CONTOUR / 2 + K.GAP_MARK + MEDIUM / 2 + 1.2
    by = ey - 14.5 - brow_lift
    lines += K.line(K.arc_sag(K.P(bx0, by + 1.2), K.P(ex0 + eye_w + 2.0, by + 3.2), 3.4), MEDIUM, role="brow")
    # nostril: a small hook springing from the contour under the nose
    tn = C.Turtle(fr - nose_len + nostril[0], nb + nostril[1], nostril[2])
    tn.arc(nostril[3], nostril[4])
    lines += K.line(tn.d(), MEDIUM, role="nose")
    # mouth: from the corner notch on the contour back into the cheek, a faint lift
    lines += K.line(K.arc_sag(K.P(fr + 0.2, my + 0.4), K.P(fr + mouth_len, my + 0.2), -1.0), MEDIUM, role="mouth")
    anchors = dict(center=K.P(cx, cy), axis=ex0 + eye_w / 2, front=fr, eye=K.P(ex0 + eye_w / 2, ey), eye_y=ey,
                   brow_y=by, nose_y=nb, mouth_y=my, lip_y=my + 4.8, chin=K.P(fr + 0.8, my + 16.0), top=top, r=r,
                   nape=K.P(cx + 23.0, ey + 32.0), neck_y=my + 62.0, throat=K.P(fr + 19.0, my + 27.0),
                   ear=K.P(cx + r * 0.20, ey + 9.0), crown_y=cy - r * 0.55, turn=0, facing=-1)
    return K.Face(d, K.R(d), lines, anchors, K._count(lines))
