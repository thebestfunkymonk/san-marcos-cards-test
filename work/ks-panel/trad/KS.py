"""K♠ · The King Beneath (brief §H.1) — "traditional pattern, re-skinned".

Construction logic of the English-pattern King (frontal head under a tall
crown, broad collar across the shoulders, robe in bold colour blocks with a
patterned front, one hand on an upright attribute, one on the orb), rebuilt
for HEADWATERS with the §H.1 attributes. Drawn as the TOP HALF only; the
system clips at y 511, adds the 180° copy, frame, band, medallion, pips.

COMPOSITION PLAN (final; card px, art window x 139–611, y 55–511; axis x 375)
------------------------------------------------------------------------
crown      Escarpment Crown. Gold band y 150–178 (top x 311–439, bottom
           x 318–432) with six Aquifer beads and the brow jewel (Source
           Rosette r 13 at (375, 164), Gill Red Ø8.4 centre). Five abutting
           limestone merlons rise from the band in three fault-steps:
           outer 25 w → y 130, middle 22 w → y 114, centre 34 w → y 98
           (crown top). Each merlon: FINE bedding line, lower course
           hatched 45°, mirrored about the axis (centre block jointed).
head       face egg hairline 160 → chin 290, half-width 50 (x 325–425).
           eye line 212 (eyes at x 350 / 400), brows ≈ 192, nose ridges
           203 → 240, moustache 250–260, mouth 267, lower lip 275. 11
           strokes + 2 pupils (§H.0 face kit, trad_kit.face).
hair       gold bell each side, x 279–348, from under the band to three
           rounded lock-ends at y 314–326; one current line per lock ending
           in a Ø6.3 terminal at the lock-end's centre.
beard      forked, gold: sideburns y 229 round the mouth to two points
           (357, 351) / (393, 351), fork notch y 317; three current lines a
           side converging on the fork (the middle one ends in a terminal).
lining     Gill Red: a pelerine collar over the shoulders (neck y 292,
           tips x 194 / 556, lower edge y 358–371) running into two lapels
           (x 298–342 at the band) with a knocked-out inline and a column of
           rising bubbles (§G.9) — the aquifer's bubbles.
clasp      simplified Lion Mark coin Ø40 at (375, 384) (local stand-in).
mantle     Spring Jade + Aquifer strata (§G.11: 12/19 courses, thin ones
           hatched), shoulders y ≈ 305–330 spanning x 153–597, sides to
           x 145 / 605 at the band; one diagonal fault (150,318)→(600,440)
           with a 12 px jog, visible across the right chest.
tunic      paper + karst voids (§G.12), the largest water-filled (jade),
           x 351–399 under the clasp widening to 342–408 at the band.
orb        viewer's left: gold sphere r 30 at (298, 408), ripple latitudes
           spreading from a vent collar, one ringed bubble for the cross;
           grasped from below (fingertips over the front, thumb on the
           inner edge); jade bell sleeve with current-line folds, red cuff.
sceptre    viewer's right: x 540, shaft 18 w, seven banded segments
           (strata / chert vesicas / marl dashes) from y 168 to the band;
           lobed rosette finial R 34 at (540, 122); fist at (540, 440)
           round the shaft, jade bell sleeve + red cuff.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import shapely
from shapely.geometry import Point, Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import tokens as T                       # noqa: E402
from deck.motifs import core as MC                 # noqa: E402
from deck.motifs.core import Frag                  # noqa: E402

from trad_kit import shapes as SH                  # noqa: E402
from trad_kit import face as FK                    # noqa: E402
from trad_kit import locks as LK                   # noqa: E402
from trad_kit import hands as HK                   # noqa: E402
from trad_kit import regalia as RG                 # noqa: E402
from trad_kit import garments as GM                # noqa: E402
from trad_kit.scene import Scene, Item             # noqa: E402

CX = 375.0
GOLD, RED, JADE, INK = T.FOIL, T.RED, T.JADE, T.INK
C, M_, F_ = T.CONTOUR, T.MEDIUM, T.FINE

FACE = FK.FaceSpec(cx=CX, eye_y=212, top=160, chin=290, half_w=50, nose_len=28,
                   mouth_y=267, lower_lip=8.0, nose_top=203.0, bridge=5.5, eye_dx=25.0,
                   crease=False, brow_gap=11.5, brow_rise=3.6, brow_slope=2.0)


# ---------------------------------------------------------------------------
# crown: gold band + five limestone merlons stepping up to a centre peak
# ---------------------------------------------------------------------------
CROWN = dict(band=(150, 178, 64, 57), steps=[(34, 52), (22, 36), (25, 20)], jewel=(164, 13))


def crown_items():
    y0, y1, hwt, hwb = CROWN["band"]
    band = RG.crown_band(CX, y0, y1, hwt, hwb)
    blocks = RG.stepped_merlons(CX, y0, CROWN["steps"])
    items = []
    for k, (poly, box) in enumerate(blocks):
        items.append(Item(f"merlon{k}", poly, GOLD, inner=M_, detail=RG.merlon_hatch(box, CX)))
    jy, jr = CROWN["jewel"]
    disc, dot, det = RG.jewel(CX, jy, jr)
    items.append(Item("band", band, GOLD, inner=M_, detail=RG.band_beads(CX, jy, hwb, jr)))
    items.append(Item("jewel", disc, GOLD, inner=M_, detail=det))
    items.append(Item("jewel_dot", dot, RED, outer=None, inner=None))
    return items


# ---------------------------------------------------------------------------
# hair: a gold mass each side, behind the face, ending in three rounded lock
# ends; lock divisions + one terminal current line per lock (§G.24)
# ---------------------------------------------------------------------------
HAIR_BODY = [(348, 170), (324, 169), (318.3, 178.5), (306, 199), (297, 228), (289, 264), (280, 300), (348, 300)]
HAIR_ENDS = [(279, 303, 314), (303, 327, 320), (327, 351, 326)]      # lock-end curls (x0, x1, bottom)
HAIR_LINES = [  # current lines (left side): from under the crown to the centre of a lock end
    [(325, 182), (314.5, 202), (306.5, 230), (299.5, 263), (291, 302)],
    [(333, 180), (324, 206), (317, 238), (312, 272), (315, 308)],
    [(343, 181), (334, 212), (329, 246), (329, 280), (339, 314)],
]


def hair_items():
    reg = LK.lock_mass(HAIR_BODY, HAIR_ENDS)
    det = Frag()
    for pts in HAIR_LINES:
        det += LK.strand(pts)
    items = []
    for side in (-1, 1):
        r = reg if side < 0 else SH.mirror_geom(reg)
        d = det if side < 0 else det.mirror_x(CX)
        items.append(Item(f"hair{side}", r, GOLD, detail=d))
    return items


def face_item():
    g = FK.face_outline(FACE)
    return Item("face", g, None, detail=FK.face_features(FACE))


# ---------------------------------------------------------------------------
# beard (forked, gold current lines) + moustache (flat gold)
# ---------------------------------------------------------------------------
BEARD_L = [(CX, 285), (364, 285), (354, 279), (345, 268), (337, 252), (331, 229),
           (324, 231), (321, 260), (326, 290), (336, 314), (347, 334), (357, 351),
           (364, 337), (370, 325), (CX, 317)]
BEARD_GUIDE = [(329, 214), (322, 250), (326, 288), (338, 318), (359, 356)]


def beard_items():
    g = SH.bilateral_poly(SH.spline(BEARD_L))
    P = LK.guide(BEARD_GUIDE)
    det = LK.current_lines(P, [7.0, 14.0, 21.0], starts=[0.0, 0.0, 0.0], ends=[1.0, 0.86, 1.0],
                           converge=0.35, terminals=[False, True, False])
    det = det + det.mirror_x(CX)
    return [Item("beard", g, GOLD, detail=det)]


def moustache_items():
    left = [(CX, 251.5), (367, 250.5), (357, 252.5), (348.5, 257.5), (342.5, 265), (340, 276),
            (344.5, 269), (351, 263.5), (360, 260.5), (369, 259.7), (CX, 260.2)]
    g = SH.bilateral_poly(SH.spline(left))
    return [Item("moustache", g, GOLD, inner=M_)]


# ---------------------------------------------------------------------------
# robe: mantle (jade strata), red collar + lapels (lining), tunic (karst)
# ---------------------------------------------------------------------------
MANTLE_L = [(CX, 296), (336, 298), (290, 305), (236, 309), (192, 316), (166, 330),
            (153, 356), (148, 410), (146, 470), (145, 525)]
LINING_L = [(CX, 292), (336, 294.5), (290, 301.5), (238, 305.5), (213, 309.5), (199, 318), (194, 338),
            (210, 358), (252, 368), (292, 371), (298, 380), (301, 440), (303, 525)]
TUNIC_L = [(CX, 372), (351, 375), (346, 440), (342, 525)]
FAULT = ((150, 318), (600, 440))
STRATA_BANDS = [(290, 540)]      # full strata over the mantle (one band)
LAPEL_X = 322.5


def lining_shape(stepped=False):
    """The mantle's red lining: a pelerine collar over the shoulders running
    into two lapels. With ``stepped`` its lower edge descends to the lapels in
    three fault-steps (§G.10) — the Balcones escarpment, echoing the crown."""
    if not stepped:
        return _bil(LINING_L)
    top = SH.spline([(CX, 292), (336, 294.5), (290, 301.5), (238, 306), (212, 316), (196, 334)])
    # collar tip, then the stepped lower edge (outer to inner): treads fall toward the lapel
    tip = SH.spline([(196, 334), (194, 342), (200, 350)])
    steps = np.array([(200, 350), (236, 350), (236, 360), (268, 360), (268, 370), (298, 370),
                      (298, 380)], float)
    lapel = np.array([(298, 380), (301, 440), (303, 525)], float)
    left = np.vstack([top, tip[1:], SH.runs(("l", steps), closed=False)[1:],
                      SH.runs(("l", lapel), closed=False)[1:], [(CX, 525)]])
    return SH.bilateral_poly(left)


def _bil(pts, straight_tail=1):
    head = SH.spline(pts[:-straight_tail]) if len(pts) - straight_tail > 1 else np.array(pts[:1], float)
    tail = np.vstack([SH.seg(a, b) for a, b in zip(pts[-straight_tail - 1:-1], pts[-straight_tail:])])
    return SH.bilateral_poly(np.vstack([head, tail, [(CX, pts[-1][1])]]))


def robe_items():
    m = _bil(MANTLE_L)
    lin = lining_shape()
    tun = _bil(TUNIC_L)

    def lining_ko(vis):
        f = GM.inline(lin, 7.0, T.MEDIUM)
        for s in (-1, 1):
            x = LAPEL_X if s < 0 else 2 * CX - LAPEL_X
            f += RG.bubble_column(x, 508, 392, d0=5.5, ratio=1.2, w=T.MEDIUM)
        return MC.clip(f, vis)

    mantle = Item("mantle", m, JADE, detail=lambda vis: GM.strata_bands(vis, STRATA_BANDS, fault=FAULT,
                                                                       y0=300, jog=12.0, edge_w=T.MEDIUM))
    lining = Item("lining", lin, RED, knock=lining_ko)
    voids, water, ceil = GM.flooded_voids(tun, origin=(CX, 404), pitch=(22.0, 16.5), margin=5.2,
                                          weights=(0.30, 0.34, 0.36), seed=1966, min_d=9.5)
    tunic = Item("tunic", tun, None, detail=voids)
    caverns = Item("caverns", water, JADE, outer=T.FINE, inner=T.FINE, detail=ceil)
    return [mantle, lining, tunic, caverns]


def _cuff(wrist, direction, length=16.0, width=26.0):
    a = np.radians(direction)
    u = np.array([np.cos(a), np.sin(a)])
    p0 = np.asarray(wrist) - u * 3
    return SH.ribbon(np.vstack([p0, p0 + u * length]), width, width + 2, cap1="flat")


def _sleeve(wrist, direction, length=60.0, width=30.0):
    a = np.radians(direction)
    u = np.array([np.cos(a), np.sin(a)])
    p0 = np.asarray(wrist) + u * 8
    return SH.ribbon(np.vstack([p0, p0 + u * length]), width, width + 6, cap1="flat")


ORB = (298, 408, 30)


def bell_sleeve(wrist, elbow, w_wrist, w_elbow, cuff_len=15.0, mantle=None, folds=3):
    """Forearm in a jade bell sleeve running from the elbow (at the mantle's
    edge) to the wrist, ending in a flared, turned-back red cuff (the
    mantle's lining). The sleeve carries ``folds`` FINE current lines
    (§G.24) as drapery, ending in terminals short of the cuff.
    Returns (sleeve, cuff, folds Frag)."""
    wrist, elbow = np.asarray(wrist, float), np.asarray(elbow, float)
    u = (wrist - elbow) / np.hypot(*(wrist - elbow))
    g = SH.seg(elbow - u * 40, wrist)
    sleeve = SH.ribbon(g, w_elbow, w_wrist, cap1="flat")
    c0, c1 = wrist - u * cuff_len, wrist + u * 2.0
    cuff = SH.ribbon(SH.seg(c0, c1), w_wrist + 2, w_wrist + 9, cap1="flat")
    cuff = cuff.buffer(2.5, quad_segs=8).buffer(-2.5, quad_segs=8)
    f = Frag()
    for j in range(folds):
        off = (j - (folds - 1) / 2) * 13.0          # parallel folds along the forearm
        f += LK.current_lines(SH.seg(elbow - u * 40, c0 - u * (10 + 7 * abs(j - (folds - 1) / 2))), [off],
                              converge=0.0, terminals=True)
    if mantle is not None:
        m = SH.shp(mantle)
        sleeve, cuff = sleeve.intersection(m), cuff.intersection(m)
    return sleeve, cuff, f


def orb_items():
    ox, oy, r = ORB
    sphere, bub, collar, det = RG.spring_orb(ox, oy, r)
    h = HK.cup(ox, oy, r, side=-1, wrist_dir=150)
    wx, wy = h["wrist"]
    sleeve, cuff, folds = bell_sleeve((wx + 5, wy - 3), (150, wy + 56), 54, 120, cuff_len=20,
                                      mantle=_bil(MANTLE_L))
    return [Item("orb_sleeve", sleeve, JADE, inner=M_, detail=folds),
            Item("orb_cuff", cuff, RED),
            Item("orb_collar", collar, GOLD, inner=M_), Item("orb", sphere, GOLD, detail=det),
            Item("orb_bubble", bub, None, inner=M_),
            Item("orb_hand", h["hand"], None, detail=h["lines"]),
            Item("orb_thumb", h["thumb"], None)]


def sceptre_items():
    shaft, collars, det = RG.banded_shaft(540, 168, 525, 18, n=7, collar=7.0, collar_w=18)
    R = 34.0
    finial, fin_det = RG.rosette_finial(540, 122, R, lobes=10)
    neck = SH.smooth_poly(shapely.box(528, 150, 552, 170), 3)
    h = HK.fist(540, 440, staff_w=18, side=1, wrist_dir=74)
    wx, wy = h["wrist"]
    sleeve, cuff, folds = bell_sleeve((wx - 2, wy - 8), (606, wy + 60), 44, 100, cuff_len=20,
                                      mantle=_bil(MANTLE_L), folds=2)
    return [Item("sc_sleeve", sleeve, JADE, inner=M_, detail=folds),
            Item("shaft", shaft, GOLD, outer=M_, detail=det), Item("collars", collars, GOLD, outer=M_, inner=M_),
            Item("neck", neck, GOLD), Item("finial", finial, GOLD, detail=fin_det),
            Item("sc_cuff", cuff, RED),
            Item("sc_hand", h["hand"], None, detail=h["lines"]),
            Item("sc_thumb", h["thumb"], None)]


def clasp_item():
    shape, det, _ = RG.lion_mark(CX, 384, 40)
    return Item("clasp", shape, GOLD, inner=M_, detail=det)


def PARTS():
    """Back-to-front stacking of the figure (each entry a list of Items)."""
    return [robe_items(), hair_items(), [face_item()], beard_items(), moustache_items(),
            crown_items(), [clasp_item()], sceptre_items(), orb_items()]


def scene() -> Scene:
    sc = Scene()
    for part in PARTS():
        sc.add(*part)
    return sc


def build():
    frag, _ = scene().render()
    return frag.layers()
