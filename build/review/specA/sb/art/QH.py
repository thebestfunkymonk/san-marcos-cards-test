"""THROWAWAY review test (build/review/specA) — a minimal court module written
only from deck/ART_CONTRACT.md, to test that the contract is complete."""
from deck import tokens as T, frames as F
from deck.cardsvg import layers_merge
from inkkit import geom as G, svg as S
from deck import motifs as M

def build():
    # robe: jade fill + Aquifer CONTOUR silhouette, runs past 511 (system clips)
    robe = G.poly_d([(200, 330), (550, 330), (575, 530), (175, 530)], closed=True)
    # red bodice panel with ripple rings knocked out (geometric, §5)
    bodice = G.poly_d([(330, 340), (420, 340), (430, 530), (320, 530)], closed=True)
    rings = M.stroke(G.circle_d(375, 420, 14) + G.circle_d(375, 420, 24), T.MEDIUM)
    bodice_ko = M.knockout(bodice, rings)
    # jade robe must not show under red (red prints above jade: fine) ;
    # half-hatch the left half of the robe in Aquifer FINE
    hat = M.half_hatch(robe, "left", color=T.INK)
    # head (paper skin), CONTOUR
    head = G.ellipse_d(375, 230, 44, 56)
    # crown: flat gold fill with Aquifer contour
    crown = G.poly_d([(335, 175), (345, 120), (375, 150), (405, 120), (415, 175)], closed=True)
    # sceptre on viewer's right, x 545, from y 110 into the band
    sceptre = G.poly_d([(545, 110), (545, 540)])
    lion = F.lion_mark_fragments(375, 360, 40)   # contract §3.1 hook (gold clasp)
    fills = {"jade": [S.path(robe, fill=T.JADE)],
             "red": [S.path(bodice_ko, fill=T.RED)],
             "gold": [S.path(crown, fill=T.FOIL)]}
    lines = {"ink": [S.path(robe + head + crown, fill="none", stroke=T.INK, stroke_width=T.CONTOUR,
                            stroke_linejoin="round", stroke_linecap="round"),
                     S.path(bodice, fill="none", stroke=T.INK, stroke_width=T.MEDIUM, stroke_linejoin="round")],
             "gold": [S.path(sceptre, fill="none", stroke=T.FOIL, stroke_width=T.RULE, stroke_linecap="round")]}
    return layers_merge(fills, hat.layers(), lines, lion)
