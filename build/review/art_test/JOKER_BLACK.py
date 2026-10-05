"""Throwaway Little Joker per contract §3.3: Aquifer body, gold eye ring, jade half-hatch tract (§H.18)."""
from deck import tokens as T, frames as F
from deck.cardsvg import layers_merge
from inkkit import geom as G, svg as S
def build():
    body = G.ellipse_d(375, 400, 120, 160)
    eye_ring = G.circle_d(420, 300, 14)
    tract = "".join(G.poly_d([(300 + k * 7, 380), (330 + k * 7, 470)]) for k in range(8))
    return layers_merge(
        {"ink": [S.path(body, fill=T.INK), S.path(G.circle_d(420, 300, 5), fill=T.INK)]},
        {"gold": [S.path(eye_ring, fill="none", stroke=T.FOIL, stroke_width=T.FINE)]},
        {"jade": [S.path(tract, fill="none", stroke=T.JADE, stroke_width=T.FINE, stroke_linecap="butt")]},
        {"gold": F.joker_rule_fragments()})
