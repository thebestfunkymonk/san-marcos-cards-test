"""K♠ · The King Beneath (brief §H.1) — compass & ruler construction.

Every contour is a circle, a circular arc, a straight line or a vesica; the
frontal elements are drawn as the viewer's-left half and mirrored about
x = 375. The figure is assembled in a painter's-order Scene (kit.py) that
hides what lies behind each object geometrically, adds the CONTOUR
silhouette, and heals §I.12 gaps.

Composition plan (card px; top half only — art window x 139–611, y 55–511):

    crown     Escarpment Crown: gold band y 162–188 whose ends are rays from
              (375, 700); five gold limestone merlons on the same rays, tops
              134 / 111 / 88 (three fault-steps), crenels 10.6+ px; outer
              halves hatched 45°, the centre merlon's cap bedded; brow jewel
              = 8-rib rosette r 14 with a red Ø8.4 core. Overall x 302–448.
    head      Moss egg r 44 about (375, 206): top 162, widest 206, chin 276
    eyes      y 213, centres x 354 / 396; vesica 24 wide, lid sag 3.6 (RULE),
              lower sag 5 (FINE), Ø6.3 pupils tucked 0.9 below the line
    brows     arcs at y ≈ 200; nose ridges 208–240 converging to the brow,
              hooks r 4.2; lower-lip tick y 267 (the moustache is the lip line)
    hair      two lock fans (circle through (323,176), (299,250), (313,326)),
              6 ribbons of 7 px, rolled ends at y ≈ 330
    beard     two pie-slice fans, centre (390.7, 279.0) r 72.9 and mirror: the
              fork edge is a radius; tips (354 / 396, 342), notch 306; x 318–432
    moustache two vesica leaves (371.5, 251.5) → (344, 264), width 10
    morse     winged Lion Mark clasp (375, 376): mane Ø39, span 81 × 39
    tunic     vesica, tips (375, 318) and (375, 732), half-width 23 at y 525
              (R 943) — the Spring Lake lens through the card centre
    lapels    red, 56 wide at the waist, broadening to a shawl collar at the
              shoulder (x 278), bubbles rising Ø4.2 → 12.6 knocked out to paper
    mantle    tangent arc chain from (375, 300): yoke r 620 / 12°, run 30,
              shoulder r 72, then straight down; x 160 at the band; 16 px plain
              border + FINE seam; strata 12/19 with the fault (190,505)→(268,318)
    orb       (298, 420) r 33, three ripple latitudes, bubble finial; held by a
              concentric hand sector; left sleeve rises from the band at x 232
    sceptre   x 540, 22 wide, finial rosette (540, 114) r 29 on a knop, seven
              segments marl / strata / chert; fist (540, 424) gripped from the
              body side; right sleeve rises from (478, 540) to the wrist (507, 458)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import kit as K                       # noqa: E402
import face as FC                     # noqa: E402
import hair as H                      # noqa: E402
import regalia as RG                  # noqa: E402
import garments as GM                 # noqa: E402
import hands as HD                    # noqa: E402
from deck.motifs import core as C     # noqa: E402
from deck import frames as F          # noqa: E402

AX = K.AX
ORB_C, ORB_R = (298.0, 420.0), 33.0
FIST = (540.0, 424.0)
RWRIST = (507.0, 458.0)
RSLEEVE_BASE = (478.0, 540.0)
HALO = 4.3          # paper channel around attributes and hands (Drifters treatment; ≥ 4.2 where lines run parallel)


def figure():
    sc = K.Scene()
    # the moustache's lower edge is the lip line (11 face strokes)
    fs = FC.FaceSpec(mouth_bow=False, lip_y=267.0, lip_hw=5.5)
    ls = GM.LensSpec()

    # ---- body -------------------------------------------------------------
    mant = GM.mantle()
    sc.add("mantle", mant.frag, mant.shape)
    tun = GM.tunic(ls)
    sc.add("tunic", tun.frag, tun.shape)
    for side in (-1, 1):
        lp = GM.lapel(ls, side, mant.shape)
        sc.add(f"lapel{side}", lp.frag, lp.shape)

    # ---- head -------------------------------------------------------------
    for side in (-1, 1):
        hf = H.hair_fall(fs, side=side)
        sc.add(f"hair{side}", hf.frag, hf.shape)
    f = FC.face(fs)
    sc.add("head", f.lines + K.outline(f.head), f.skin)
    bd = H.beard_forked(fs)
    sc.add("beard", bd.frag, bd.shape, halo=HALO, halo_skip=("head",))
    mo = H.moustache(fs)
    sc.add("moustache", mo.frag, mo.shape, halo=HALO, halo_skip=("head",))
    cr = RG.escarpment_crown()
    sc.add("crown", cr.frag, cr.shape)
    cl = RG.lion_clasp((AX, 376))
    sc.add("clasp", cl.frag, cl.shape, halo=HALO)

    # ---- arms and attributes ------------------------------------------------
    # Both forearms rise from the waist band toward the viewer's right (a C2
    # pinwheel once the card is two-headed): the left to the orb, the right
    # across the body to the sceptre, gripped from the body side.
    # order: sleeves, sceptre, orb, cuffs, then the hands over the cuffs
    slL, cfL = GM.sleeve(GM.SleeveSpec())
    slR, cfR = GM.sleeve(GM.SleeveSpec(base=RSLEEVE_BASE, wrist=RWRIST, sag=-8.0, width=46.0, wrist_w=24.0))
    sc.add("sleeveL", slL.frag, slL.shape)
    sc.add("sleeveR", slR.frag, slR.shape)
    sp = RG.core_sceptre()
    sc.add("sceptre", sp.frag, sp.shape, halo=HALO)
    orb = RG.vent_orb(ORB_C, ORB_R)
    sc.add("orb", orb.frag, orb.shape, halo=HALO)
    sc.add("cuffL", cfL.frag, cfL.shape)
    sc.add("cuffR", cfR.frag, cfR.shape)
    hu, thL = HD.hand_under_sphere(ORB_C, ORB_R, wrist=(276.0, 462.0))
    sc.add("handL", hu.frag, hu.shape, halo=HALO, halo_skip=("cuffL", "sleeveL", "orb"))
    fi, thR = HD.fist_on_shaft(*FIST, back=-1, wrist=RWRIST, wrist_w=24.0)
    sc.add("handR", fi.frag, fi.shape, halo=HALO, halo_skip=("cuffR", "sleeveR"))
    sc.add("thumbR", thR.frag, thR.shape, halo=HALO, halo_skip=("handR",))
    # the rank medallion (system-drawn at the card centre, mask r 33.25): an
    # invisible occluder with a halo, so every line stops cleanly clear of
    # the band rules where they end at the medallion
    sc.add("medallion", C.Frag(), K.R(K.circle((AX, 525.0), F.medallion_radius("K"))), sil=False, halo=3.2)
    return sc


def build():
    sc = figure()
    art = sc.compose()
    return art.layers()
