"""K♠ · The King Beneath (brief §H.1) — illustrator's construction.

Drawn the way an illustrator sketches: a coordinate plan first (below), then
every organic silhouette authored as hand-placed cubic Béziers with tangent
handles (bez.K), composed back-to-front in a Scene with geometric occlusion
(scene.py). The reusable kit lives beside this file: face.py (face kit),
hands.py (mitten fist / cupping hand), hair.py (current lines), regalia.py
(crown base, jewel, orb, core sceptre, Lion Mark roundel, clean hatch),
garment.py (bell sleeves, folds, standing collar, revers, strata band,
bubble columns).

COMPOSITION PLAN (art window x139–611, y55–511; frontal, axis x = 375)
  crown    Escarpment Crown: gold band y150.4–176.4, x289.4–460.6; five
           battered limestone merlons 26 w (2 px taper) / 10.8 gaps, half-
           hatched; tops 128 (outer) · 112 · 96 (centre peak) — three steps
           brow jewel: small Source Rosette r12 on the band's lower edge,
           Gill Red Ø8.4 centre
  head     egg 94 × 116: top 166 (under the band), brow 198, eye line 210,
           nose base 245, mouth 271, lip 279, chin 300 (under the beard)
  hair     gold mass x 290–350 from under the band to a turned-under end at
           y≈314, one §G.24 current bundle per side
  beard    gold, forked: cheek line (327,226)→(345,262); lobe tips
           (350,362)/(400,362); notch (375,338); moustache 252–286
  collar   standing fan collar behind the head: red lining, jade turned rim;
           flared corners (239,205)/(511,205), foot on the shoulders y≈333
  mantle   jade; neck (375,298); shoulders y≈336 (x 173–577); strata band on
           the shoulders y 330–392 with one diagonal fault jog; plain below
  revers   red turned-back lining (⟩⟨) meeting at the clasp centre; outer
           edges (258/492, band) → (334/416, 392); rising knocked-out bubbles
  clasp    Lion Mark roundel Ø39.6 at (375, 389)
  tunic    paper with karst voids, above and below the clasp
  L arm    bell sleeve from the band (x180–306) to its red-lined mouth
           (276, 461); the hand cups the orb (318, 416) r33 from below
  R arm    sleeve rising under the fist; mouth (574, 455)
  sceptre  x 540, 21 w, from the band to its rosette finial (centre y124,
           top 98); seven banded segments (strata · chert · marl …);
           the fist grips it at (540, 428)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import shapely                                    # noqa: E402

from deck import tokens as T                      # noqa: E402
from deck.motifs import core as MC                # noqa: E402
from deck.motifs import geometric as MG           # noqa: E402
from inkkit import geom as G                      # noqa: E402

from bez import K, path, pts, sym                 # noqa: E402
from scene import Scene, Part                     # noqa: E402
import face as FK                                 # noqa: E402
import garment as GM                              # noqa: E402
import hair as HK                                 # noqa: E402
import hands as HD                                # noqa: E402
import regalia as RG                              # noqa: E402

CX, EY = 375.0, 210.0
BAND = 525.0          # draw past the band's top rule; the system clips at 511
SEAM = T.MEDIUM       # garment seams inside the figure; the silhouette is CONTOUR

SPEC = FK.FaceSpec(nose_base=35.0, mouth_y=61.0, lip_y=69.0, chin=90.0, jaw_w=84.0)
CLASP = (CX, 389.0)
ORB = (318.0, 416.0, 33.0)
SCEPTRE_X = 540.0
FIST = (SCEPTRE_X, 428.0)

# sleeve mouths ((centre), rx ⊥ forearm, ry, rotation)
MOUTH_L = ((276.0, 461.0), 36.0, 15.5, 40.0)
MOUTH_R = ((574.0, 455.0), 27.0, 13.0, -8.0)


# ---------------------------------------------------------------------------
# silhouettes (hand-placed knots; left halves mirrored where symmetric)
# ---------------------------------------------------------------------------
def collar():
    return GM.standing_collar(
        [K(CX, 250, 180, lo=40),
         K(298, 230, 197, li=30, lo=20),
         K(239, 205, ai=202, ao=100, li=22, lo=26),        # flared corner
         K(232, 300, 95, li=30, lo=14),
         K(245, 334, ai=70, ao=0, li=14),
         K(CX, 322, 0)],
        [K(224, 218, ao=18, lo=22), K(298, 244, 16, li=26, lo=30), K(CX, 264, 0, li=40)])


def mantle_sil():
    # the shoulder runs nearly level where the sceptre crosses it (x≈530–556,
    # mirrored ≈194–220), so the outline meets the shaft square: no ink knot
    return sym([K(CX, 298, 180, lo=40),
                K(290, 314, 172, li=30, lo=30),
                K(206, 336, 174, li=30, lo=12),
                K(184, 364, 112, li=16, lo=20),
                K(173, 412, 96, li=22, lo=34),
                K(166, BAND, ai=93, ao=0, li=30),
                K(CX, BAND, 0)])


def revers_sil(side=-1):
    return GM.revers((348, 316), CLASP, (340, BAND), BAND, 258, (334, 392), (342, 316), side=side)


def tunic_sil():
    return path([K(322, 300), K(428, 300), K(462, BAND), K(288, BAND)], closed=True)


def moustache_sil():
    return sym([K(CX, 252.5, 180, lo=7),
                K(354, 254, 168, li=7, lo=9),
                K(333, 266, 128, li=8, lo=6),
                K(322, 285, ai=110, ao=60, li=6, lo=3),        # tip, curling in
                K(329, 286, -40, li=3, lo=6),
                K(342, 274, -30, li=6, lo=7),
                K(360, 265, -12, li=7, lo=6),
                K(CX, 263, ai=0, li=6)])


def beard_sil():
    return sym([K(CX, 290, 180, lo=8),
                K(357, 285, ai=195, ao=240, li=8, lo=5),
                K(345, 262, ai=250, ao=235, li=8, lo=14),      # tucked under the moustache
                K(327, 226, ai=250, ao=180, li=18, lo=3),      # up the cheek to the temple
                K(318, 232, ai=100, ao=96, li=3, lo=16),
                K(313, 282, 90, li=18, lo=20),
                K(324, 326, 55, li=18, lo=14),
                K(350, 362, ai=62, ao=14, li=16, lo=4),        # lobe tip
                K(CX, 338, ai=-60, li=13)])


def beard_lines(bsil):
    """One §G.24 current bundle per lobe (3 FINE lines), mirrored."""
    g = HK.guide([K(329, 240, 96, lo=16), K(328, 290, 86, li=18, lo=16), K(349, 350, 60, li=14)])
    fl = HK.bundle(g, 3, side=+1, offset0=2.0, t0=0.0, t1=0.9, stagger=0.06, clip=bsil)
    return fl + fl.mirror_x(CX)


def hair_mass():
    """Left hair mass: one silhouette falling from under the band past the
    temple to a rounded, turned-under end at the jaw, and a §G.24 current
    bundle (3 FINE lines) that follows the outer edge and curls under with
    it, each line ending in a Ø6.3 terminal."""
    sil = path([K(318, 160, ai=0, ao=98, lo=12),
                K(303, 214, 100, li=26, lo=22),
                K(292, 268, 95, li=22, lo=16),
                K(290, 296, 84, li=12, lo=8),
                K(304, 314, 5, li=10, lo=10),                  # rounded, turned-under end
                K(326, 304, -50, li=10, lo=10),
                K(338, 280, -84, li=14, lo=24),                # inner edge, behind the beard
                K(348, 200, -94, li=30, lo=20),
                K(350, 160, ai=-90, ao=180)], closed=True)
    guide = pts([K(316, 170, 101, lo=18), K(302, 220, 99, li=22, lo=22), K(291, 270, 95, li=20, lo=12),
                 K(291, 298, 82, li=10, lo=8), K(304, 314, 5, li=8, lo=8), K(322, 306, -60, li=8)], step=0.5)
    lines = HK.bundle(guide, 3, side=+1, offset0=9.5, t0=0.07, t1=0.97, stagger=0.1, clip=sil)
    return sil, lines


def sleeves():
    left = GM.bell_sleeve(MOUTH_L, K(180, BAND, ai=180, ao=-58, lo=30), K(306, BAND, ai=70, ao=180, li=14),
                          a_dirs=(-46, 40), b_dirs=(40, 72), a_li=34, b_lo=12, cuff=15.0)
    left["folds"] = (GM.fold([K(210, 524, -58, li=10, lo=14), K(234, 488, -52, li=12, lo=10),
                              K(248, 470, -44, li=8)], left["cuff_edge"]) +
                     GM.fold([K(242, 525, -58, li=8, lo=12), K(262, 494, -50, li=10)], left["cuff_edge"]))
    right = GM.bell_sleeve(MOUTH_R, K(544, BAND, ai=180, ao=-92, lo=20), K(599, BAND, ai=92, ao=180, li=20),
                           a_dirs=(-96, -8), b_dirs=(-8, 86), a_li=24, b_lo=20, cuff=14.0)
    right["folds"] = GM.fold([K(572, 524, -88, li=8, lo=10), K(576, 470, -84, li=8)], right["cuff_edge"])
    return left, right


# ---------------------------------------------------------------------------
def build():
    sc = Scene()
    face = FK.frontal_face(CX, EY, SPEC)
    sl_l, sl_r = sleeves()
    hand = HD.cup(*ORB, tips=+1)

    # 1 mantle: jade; strata across the shoulders with one diagonal fault jog
    mant = mantle_sil()
    strata, _ = GM.strata_band(mant, 318.0, 2, fault=((150, 468), (600, 334)))
    sc.add(Part("mantle", mant, fills=[(None, T.JADE)], detail=strata, contour=SEAM))

    # 2 tunic: paper with karst voids (clear of the revers and the medallion mask)
    tun = tunic_sil()
    void_reg = G.difference(tun, G.circle_d(CX, 525.0, 33.25 + 7.0), G.union(revers_sil(-1), revers_sil(1)))
    sc.add(Part("tunic", tun, detail=MG.karst_voids(void_reg, pitch=(24.0, 18.0), seed=1689,
                                                     weights=(0.3, 0.4, 0.3)), contour=None))

    # 3 collar: red lining, jade turned rim
    col = collar()
    sc.add(Part("collar", col["sil"], fills=[(col["red"], T.RED), (col["rim"], T.JADE)], contour=SEAM,
                detail=col["rim_line"]))

    # 4 revers: red lining, a column of bubbles rising (skipping what the arm covers)
    front = shapely.union_all([MC.region(d) for d in (hand.mitten, hand.thumb, G.circle_d(*ORB),
                                                      sl_l["sil"], sl_r["sil"])])
    for s in (-1, 1):
        rv = revers_sil(s)
        holes = GM.bubble_column(revers_sil(-1), y_start=505.0, y_stop=410.0, side=s, avoid=front)
        sc.add(Part(f"revers{s}", rv, fills=[(G.difference(rv, holes), T.RED)], contour=SEAM))

    # 5 hair (gold), 6 face (paper), 7 beard + moustache (gold)
    hsil, hlines = hair_mass()
    for s in (-1, 1):
        hs, hl = (hsil, hlines) if s < 0 else (G.mirror_x(hsil, CX), hlines.mirror_x(CX))
        sc.add(Part(f"hair{s}", hs, fills=[(None, T.FOIL)], detail=hl, contour=SEAM))
    sc.add(Part("face", face.sil, detail=face.lines, clip_detail=False, contour=SEAM))
    bsil = beard_sil()
    sc.add(Part("beard", bsil, fills=[(None, T.FOIL)], detail=beard_lines(bsil), contour=SEAM))
    sc.add(Part("moustache", moustache_sil(), fills=[(None, T.FOIL)], contour=T.MEDIUM))

    # 8 crown + brow jewel (edges 0.375 px off the grid so the CONTOUR edges
    #   land on pixel quarters and rsvg / resvg anti-alias alike — QA 25)
    cr = RG.crown(CX, 150.375, width=171.25, band_h=26.0, merlon_w=26.0, coping=0.0, taper=2.0,
                  tops=(128.375, 112.375, 96.375), rims=False, jewel_r=12.0)
    sc.add(Part("crown", cr.sil, fills=cr.fills, detail=cr.lines))
    j = cr.parts["jewel"]
    sc.add(Part("jewel", j.sil, fills=j.fills, detail=j.lines, contour=T.MEDIUM))

    # 9 clasp: the Lion Mark roundel, where the revers meet
    lm = RG.lion_roundel(*CLASP, 18.2)
    sc.add(Part("clasp", lm.sil, fills=lm.fills, detail=lm.lines, contour=T.MEDIUM))

    # 10 left arm: sleeve + red mouth, the orb, the cupping hand
    sc.add(Part("sleeveL", sl_l["sil"], fills=[(sl_l["body"], T.JADE), (sl_l["cuff"], T.RED)],
                detail=sl_l["folds"] + sl_l["cuff_line"], contour=SEAM))
    sc.add(Part("cuffL", sl_l["mouth"], fills=[(None, T.RED)], contour=SEAM))
    ob = RG.orb(*ORB)
    sc.add(Part("orb", ob.sil, fills=ob.fills, detail=ob.lines))
    sc.add(Part("handL", hand.mitten, detail=hand.lines, contour=SEAM))
    sc.add(Part("thumbL", hand.thumb, contour=SEAM))

    # 11 right arm: sleeve + red mouth, then the sceptre in front of it, the fist
    sc.add(Part("sleeveR", sl_r["sil"], fills=[(sl_r["body"], T.JADE), (sl_r["cuff"], T.RED)],
                detail=sl_r["folds"] + sl_r["cuff_line"], contour=SEAM))
    sc.add(Part("cuffR", sl_r["mouth"], fills=[(None, T.RED)], contour=SEAM))
    sp = RG.sceptre(SCEPTRE_X, 98.0, BAND, w=21.0, finial_r=26.0, seg_bottom=388.0)
    sc.add(Part("sceptre", sp.sil, fills=sp.fills, detail=sp.lines, contour=T.MEDIUM, in_outline=False))
    sc.add(Part("finial", sp.parts["finial"], contour=T.CONTOUR, occludes=False, in_outline=False))
    fist = HD.fist(*FIST, tips=-1)
    sc.add(Part("fistR", fist.mitten, detail=fist.lines, contour=SEAM))
    sc.add(Part("thumbR", fist.thumb, detail=fist.thumb_lines, contour=SEAM))

    return sc.compose().layers()
