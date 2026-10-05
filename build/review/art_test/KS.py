"""Throwaway reviewer court (NOT a real piece): follows deck/ART_CONTRACT.md only."""
from deck import tokens as T, frames as F
from deck.cardsvg import layers_merge
from inkkit import geom as G, svg as S
from deck import motifs as M

def build():
    # a mantle running into the band (system clips at 511)
    mantle = G.poly_d([(200, 330), (550, 330), (560, 530), (190, 530)], closed=True)
    collar = G.poly_d([(300, 300), (450, 300), (430, 350), (320, 350)], closed=True)
    crown = G.poly_d([(320, 120), (430, 120), (440, 170), (310, 170)], closed=True)
    # geometric knockout on red: stripes removed from the collar
    stripes = "".join(G.poly_d([(x, 300), (x + 20, 350)]) for x in range(310, 440, 14))
    ko = G.outline(stripes, T.MEDIUM, cap="round", join="round")
    collar_ko = G.difference(collar, ko)
    fills = {"jade": [S.path(mantle, fill=T.JADE)],
             "red": [S.path(collar_ko, fill=T.RED, fill_rule="evenodd")],
             "gold": [S.path(crown, fill=T.FOIL)]}
    hatch = M.half_hatch(mantle, "left").layers() if hasattr(M, "half_hatch") else {}
    lines = {"ink": [S.path(mantle + collar + crown, fill="none", stroke=T.INK, stroke_width=T.CONTOUR,
                            stroke_linejoin="round", stroke_linecap="round")]}
    return layers_merge(fills, hatch, lines)
