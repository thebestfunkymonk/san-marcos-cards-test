"""Throwaway reviewer BACK following ART_CONTRACT §3.4 (jade flood, geometric knockouts)."""
import os
from deck import tokens as T
from inkkit import geom as G, svg as S
def build():
    flood = G.rect_d(T.SAFE, T.SAFE, T.W - 2 * T.SAFE, T.H - 2 * T.SAFE, 18)
    R = 463.2
    lens = G.intersection(G.circle_d(181.8, 525, R), G.circle_d(568.2, 525, R))
    ko = [G.outline(G.rect_d(49.5, 49.5, T.W - 99, T.H - 99), T.RULE, cap="butt", join="miter"),
          G.outline(lens, T.FINE, join="miter", miter_limit=10)]
    # C2-only emblem: an offset pair of bars + a pinwheel of 4 bars
    bar = G.rect_d(300, 330, 40, 150)
    for d in (bar, G.rotate180(bar, 375, 525)):
        ko.append(G.outline(d, T.FINE))
    blade = G.poly_d([(375, 525), (470, 470), (480, 490)], closed=True)
    import math
    for k in range(4):
        ko.append(G.outline(G.transform(blade, (math.cos(k*math.pi/2), math.sin(k*math.pi/2), -math.sin(k*math.pi/2), math.cos(k*math.pi/2),
                  375 - 375*math.cos(k*math.pi/2) + 525*math.sin(k*math.pi/2), 525 - 375*math.sin(k*math.pi/2) - 525*math.cos(k*math.pi/2))), T.FINE))
    if os.environ.get("ASYM"):
        # one asymmetric feature: a knocked-out dot of diameter ASYM (e.g. a missing darter eye in one copy)
        dd = float(os.environ["ASYM"]); ko.append(G.circle_d(470, 300, dd / 2))
    return {"jade": [S.path(G.difference(flood, *ko), fill=T.JADE)]}
