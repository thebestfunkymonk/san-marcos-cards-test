"""art/_jh_face.py — the Spring Minstrel's strict profile, facing LEFT
(§H.0 face kit; §H.6 'young, eyes lowered to the strings'; the one-eyed J♥).

The same construction as the kit's profile (``courtkit._profile_face``) and
the J♠ page's (``art/_js_face.py``) — ONE G1 biarc silhouette through pinned
points with pinned tangents: crown, forehead, brow, nose root, a straight
ridge, the tip, subnasale, upper lip, chin, throat, the neck down under the
collar, nape, occiput — so all three profile courts read as one hand. Re-pinned
for a youth who is not the page:

* a round, upright forehead and a soft brow (no brow ridge);
* a straight, slender nose, the tip barely lifted — longer than the page's;
* the §H.0 kit mouth: the upper-lip bow is the contour's ONE lip plus the
  MEDIUM mouth line from the corner notch (lifting a little at the cheek);
  the lower lip is not a bump on the contour but a FINE tick springing from
  it at the hollow under the lip — lip to chin reads as two bumps, not three;
* a small round chin; a MEDIUM jaw line from the contour under the chin back
  and up to stop under the ear lobe, closing the face (the J♠'s hood and the
  K♦'s beard do this for them); the under-chin turns at the throat and the
  neck's front contour drops into the collar, so head and neck read apart;
* the eye LOWERED: the RULE lid flattened and drooping toward the front
  corner, the Ø6 pupil tucked low under it at the front — looking down and
  forward, at the bow in his hand (the bow's hair are the strings he reads);
* a calm, low brow arc; the ear ONE MEDIUM stroke — a C from the lobe round
  the helix, rolling in at the top (the beret leaves it bare; the bob of hair
  falls behind it).

Strokes: lid, lower lid, pupil, brow, nostril, mouth, lip tick, ear, jaw = 9 (≤ 14).
"""
from __future__ import annotations

import numpy as np
from shapely.geometry import Point

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM

MEDIUM, FINE, RULE, CONTOUR = K.MEDIUM, K.FINE, K.RULE, K.CONTOUR
P = K.P


def minstrel_profile(center, *, r=42.5, eye_dy=6.0, nose_len=9.6, eye_w=16.4, lid_sag=3.0, low_sag=2.2,
                     front_drop=2.4, pupil_d=6.0, pupil_x=4.3, pupil_tuck=1.6, brow_dy=-13.6, brow_sag=2.4,
                     mouth_dy=37.0, mouth_len=10.5, mouth_lift=1.2, ear_r=9.8, ear_in=4.2, ear_dx=0.20, ear_dy=9.0,
                     neck_drop=64.0, nape=21.0, crease=0.0, nostril=(5.6, 1.0, -62.0, 3.1, 150.0), lid_flick=0.0,
                     sulcus=(1.9, 7.2), chin=(-0.6, 14.0), under_chin=(8.0, 20.4), throat=(17.0, 24.0, 58.0),
                     neck_front=(20.5, 84.0), lip_tick=(8.4, 8.0, -0.4, -1.2), jaw=(6.2, 19.9, 6.0, 25.4, -5.5)):
    """→ courtkit.Face facing LEFT (head d incl. the neck, skin region,
    feature lines, anchors, stroke count)."""
    cx, cy = float(center[0]), float(center[1])
    ey = cy + eye_dy
    fr = cx - r * 0.84                    # the face's front line (brow / lips)
    top = cy - r
    nb = ey + 17.8                        # nose base (subnasale)
    my = ey + mouth_dy                    # mouth corner line
    tip = (fr - nose_len, nb - 3.6)
    root = (fr + 3.4, ey + 0.6)
    ridge = K._hd(root, tip)
    chin_p = (fr + chin[0], my + chin[1])
    uc = (fr + under_chin[0], my + under_chin[1])
    th = (fr + throat[0], my + throat[1])
    nf = (fr + neck_front[0], my + neck_drop)
    chain_pts = [
        ((cx + 4.0, top), 180.0),                    # crown of the skull
        ((fr + 6.8, cy - 27.0), 114.0),              # a round, upright forehead
        ((fr + 0.9, ey - 9.2), 100.0),               # soft brow
        (root, ridge + 8.0),                         # a shallow nose root
        (tip, ridge - 4.0),                          # a straight slender ridge, the tip barely lifted
        ((fr - nose_len + 2.8, nb + 0.4), 16.0),     # round the tip, under the nose
        ((fr - 0.6, nb + 2.0), 78.0),                # subnasale
        ((fr - 2.7, my - 3.9), 102.0),               # full upper lip: the ONE lip on the contour
        ((fr + 0.3, my + 0.4), 64.0),                # mouth corner (a soft notch)
        ((fr + sulcus[0], my + sulcus[1]), 96.0),    # the lower lip tucked back into the hollow (its tick is FINE)
        (chin_p, 106.0),                             # a small round chin, set back
        (uc, 20.0),                                  # under the chin: the jaw line springs from here
        (th, throat[2]),                             # the throat turns down ...
        (nf, neck_front[1]),                         # ... into the collar: the neck's front contour
        ((cx + nape - 3.0, my + neck_drop), -94.0),  # neck back
        ((cx + nape, ey + 33.0), -116.0),            # nape
        ((cx + r + 5.0, cy + 2.0), -88.0),           # occiput
    ]
    pts = [P(q) for q, _ in chain_pts]
    hs = [h for _, h in chain_pts]
    d, _ = FM.biarc_chain(pts, hs, closed=True)
    lines = C.Frag()
    # ---- the eye: its front ≥ 3 px + RULE/2 clear of the contour's inner edge
    ex0 = fr + 3.4 + CONTOUR / 2 + K.GAP_MARK + RULE / 2 + 1.2
    front, back = P(ex0, ey + front_drop), P(ex0 + eye_w, ey - 0.4)
    # lowered: a flattened RULE lid drooping to a LOW front corner
    lid_d = K.arc_sag(front, back, lid_sag)
    if lid_flick:
        lid_d += f"L{back[0] + lid_flick:.3f} {back[1] + lid_flick * 0.25:.3f}"
    lines += K.line(lid_d, RULE, role="lid")
    if crease:
        # the lid crease: a FINE arc over the lid, clear of it by 4.2 + the half widths
        cf, cb = front + P(2.2, -crease), back + P(-1.0, -crease + 1.2)
        lines += K.line(K.arc_sag(cf, cb, lid_sag + 1.0), FINE, role="crease")
    lo0 = P(front[0] + 2.3, front[1] + 3.1)
    lines += K.line(K.arc_sag(lo0, back + P(-0.8, 2.2), -low_sag), FINE, role="lid-lo")
    # the pupil tucked under the lid at the front: looking down and forward
    t = pupil_x / eye_w
    lid_y = front[1] + (back[1] - front[1]) * t - lid_sag * 4 * t * (1 - t)
    pu = P(front[0] + pupil_x, lid_y + RULE / 2 + pupil_d / 2 - 0.9 + pupil_tuck)
    lines += K.dot(pu, pupil_d, role="pupil")
    # ---- brow: a calm, low MEDIUM arc over the eye
    bx0 = fr + 0.9 + CONTOUR / 2 + K.GAP_MARK + MEDIUM / 2 + 1.3
    by = ey + brow_dy
    lines += K.line(K.arc_sag(P(bx0, by + 1.0), P(ex0 + eye_w + 2.6, by + 2.6), brow_sag), MEDIUM, role="brow")
    # ---- nostril: a small hook springing from the contour under the nose
    tn = C.Turtle(fr - nose_len + nostril[0], nb + nostril[1], nostril[2])
    tn.arc(nostril[3], nostril[4])
    lines += K.line(tn.d(), MEDIUM, role="nose")
    # ---- mouth (§H.0 kit): the upper-lip bow is the contour's one lip + this MEDIUM line from the corner
    # notch back into the cheek, a faint lift; the lower lip is a FINE tick under it, clear of the contour
    lines += K.line(K.arc_sag(P(fr + 0.3, my + 0.4), P(fr + mouth_len, my - mouth_lift), -1.5), MEDIUM, role="mouth")
    if lip_tick:
        # the lower-lip tick: a short FINE arc springing from the contour under the lip (joined to it,
        # like the mouth line and the nostril), running back into the cheek and sagging a little
        ldy, llen, lrise, lsag = lip_tick
        bd = K.R(d).exterior
        l0 = P(*bd.interpolate(bd.project(Point(fr + 1.0, my + ldy))).coords[0])
        lines += K.line(K.arc_sag(l0, l0 + P(llen, -lrise), lsag), FINE, role="lip")
    # ---- ear: a C opening toward the face + the FINE inner arc (the helix fold)
    ear_c = P(cx + r * ear_dx, ey + ear_dy)
    # one stroke: from the lobe round the back of the helix to the top, then
    # curling in and down inside it (the helix rolled into the concha)
    te = C.Turtle(*K.polar(ear_c, ear_r, 104.0), 104.0 - 90.0)
    te.arc(ear_r, -178.0)
    te.arc(ear_in, -150.0)
    lines += K.line(te.d(), MEDIUM, role="ear")
    if jaw:
        # the jaw (MEDIUM): springs from the contour under the chin and sweeps back and up to stop
        # under the ear lobe — it closes the face; the paper below it is the neck
        # (the start is snapped onto the silhouette's centre line so the two MEDIUM/CONTOUR strokes join)
        j0 = P(fr + jaw[0], my + jaw[1])
        bd = K.R(d).exterior
        j0 = P(*bd.interpolate(bd.project(Point(*j0))).coords[0])
        j1 = P(cx + jaw[2], ey + jaw[3])
        lines += K.line(K.arc_sag(j0, j1, jaw[4]), MEDIUM, role="jaw")
    anchors = dict(center=P(cx, cy), axis=ex0 + eye_w / 2, front=fr, eye=P(ex0 + eye_w / 2, ey), eye_y=ey,
                   brow_y=by, nose_y=nb, mouth_y=my, lip_y=my + 4.8, chin=P(chin_p), top=top, r=r,
                   nape=P(cx + nape, ey + 33.0), neck_y=my + neck_drop, throat=P(th),
                   neck_front=P(nf), under_chin=P(uc), neck_back=P(cx + nape - 3.0, my + neck_drop),
                   ear=ear_c, ear_r=ear_r, crown_y=cy - r * 0.55, turn=0, facing=-1, forehead=P(fr + 6.8, cy - 27.0))
    return K.Face(d, K.R(d), lines, anchors, K._count(lines))
