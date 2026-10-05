"""THROWAWAY system test (not art): a continuous double-headed court.

Proves deck.build's DOUBLE_HEAD = "continuous" mode: the top-half art is
clipped along a C2 seam, the 180° copy is added, and no band / partition /
medallion / seam line is drawn. Everything that crosses the seam is built
C2 (a shape unioned with its own rot180), so the halves meet invisibly.

Set the env var SEAM_TEST to choose a variant:
    clean   (default) straight 28° seam, continuous art
    curve   a custom C2 S-curve seam (left half given, system completes it)
    broken  like clean plus two deliberate breaks (a jade patch and a line
            that stop at the seam) — 10s must flag them
"""
import os

from inkkit import geom as G
from inkkit import svg as S
from deck import tokens as T
from deck.cardsvg import layers_merge

VARIANT = os.environ.get("SEAM_TEST", "clean")

DOUBLE_HEAD = "continuous"
if VARIANT == "curve":
    # left half only, ending exactly on the centre: the system adds the 180° copy
    SEAM = G.smooth_d([(120, 600), (220, 610), (300, 570), (375, 525)])
else:
    SEAM = 28            # degrees, rising to the viewer's right (also the default)

C2 = lambda d: G.union(d, G.rotate180(d))          # noqa: E731  (a shape that crosses the seam cleanly)


def _stroke(d, col, w, cap="round", join="round"):
    return S.path(d, fill="none", stroke=col, stroke_width=w, stroke_linecap=cap, stroke_linejoin=join)


def build():
    # robe: one C2 silhouette running from head to head
    robe = C2(G.poly_d([(262, 318), (488, 318), (538, 525), (488, 732), (262, 732), (212, 525)], closed=True))
    # sash: a C2 band on a line through the centre, inside the robe
    sash = G.intersection(robe, G.outline(G.poly_d([(170, 300), (580, 750)]), 46, cap="butt"))
    # stripes: a C2 pair (x and 750 - x) crossing the seam obliquely, cut under the sash
    stripes = G.poly_d([(300, 330), (300, 720)]) + G.poly_d([(450, 330), (450, 720)])
    stripes = G.clip(stripes, G.offset(robe, -(T.CONTOUR / 2 + 0.01)))
    stripes = G.clip_out(stripes, G.offset(sash, T.MEDIUM / 2 + 4.2 + T.MEDIUM / 2))
    # gold studs on the centre line, C2 positions
    studs = "".join(G.circle_d(375, 525 + k * 52, 6.3) for k in (-3, -2, 2, 3))
    studs = G.difference(studs, G.offset(sash, 4.2 + T.MEDIUM / 2))
    # head (top half only: the other head is the system's 180° copy)
    face = G.circle_d(375, 212, 52)
    crown = G.poly_d([(322, 168), (322, 112), (348, 138), (375, 100), (402, 138), (428, 112), (428, 168)],
                     closed=True)
    crown = G.difference(crown, G.offset(face, T.CONTOUR / 2 + 0.01))
    eyes = G.circle_d(355, 205, 4.2) + G.circle_d(395, 205, 4.2)
    neck = G.poly_d([(352, 262), (352, 318)]) + G.poly_d([(398, 262), (398, 318)])

    # layer trap (ART_CONTRACT §2.1): jade and gold inside the red robe are cut out of it
    red = G.difference(robe, G.union(sash, studs))
    fills = {"red": [S.path(red, fill=T.RED)],
             "jade": [S.path(sash, fill=T.JADE)],
             "gold": [S.path(crown, fill=T.FOIL), S.path(studs, fill=T.FOIL)]}
    lines = {"ink": [_stroke(robe, T.INK, T.CONTOUR), _stroke(sash, T.INK, T.MEDIUM),
                     _stroke(stripes, T.INK, T.MEDIUM, cap="butt"),
                     _stroke(studs, T.INK, T.FINE),
                     _stroke(face, T.INK, T.CONTOUR), _stroke(crown, T.INK, T.MEDIUM),
                     _stroke(neck, T.INK, T.MEDIUM), S.path(eyes, fill=T.INK)]}
    out = layers_merge(fills, lines)
    if VARIANT == "broken":
        # 1) a jade pocket drawn in the top half only: it stops dead at the seam
        pocket = G.intersection(robe, G.rect_d(232, 540, 60, 120))
        pocket = G.difference(pocket, G.offset(sash, 4.2 + T.MEDIUM))
        # 2) a hem line that ends at the seam with nothing to meet it
        hem = G.poly_d([(440, 410), (480, 500)])
        out["red"] = [S.path(G.difference(red, pocket), fill=T.RED)]
        out = layers_merge(out, {"jade": [S.path(pocket, fill=T.JADE)],
                                 "ink": [_stroke(pocket, T.INK, T.MEDIUM), _stroke(hem, T.INK, T.MEDIUM)]})
    return out
