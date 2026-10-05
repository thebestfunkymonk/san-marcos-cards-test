"""THROWAWAY review test (JH variant): contract §3.1 CUT_Y = 525 path — a paddle shaft
(attribute) that visibly crosses the band, per brief §F.1 'Attributes may run
into the band; the band hides the cut'."""
from deck import tokens as T
from inkkit import geom as G, svg as S
CUT_Y = 525
def build():
    shaft = G.rect_d(539, 100, 12, 440)          # x 539-551, runs to 540 (system clips at 525)
    return {"gold": [S.path(shaft, fill=T.FOIL)],
            "ink": [S.path(shaft, fill="none", stroke=T.INK, stroke_width=T.MEDIUM, stroke_linejoin="round")]}
