from rh import *
from dataclasses import replace
from deck.motifs import rice as RI
from inkkit import geom as G
from shapely.geometry import Point
w = RI.rice_wreath_arc(375, 470, 175)
col = {"stem": T.RED, "knot": T.JADE, "knot-tail": T.JADE, "terminal": T.JADE}
f2 = C.Frag([replace(m, color=col.get(m.role, T.INK), layer=C.LAYER_OF[col.get(m.role, T.INK)]) for m in w.marks])
show(f2, "wreath-ac-roles-3x", zoom=3)
stem = [p for m in w.marks if m.role=="stem" for p,_ in G.flatten(m.d)]
Ls = sorted(round(G.Curve(p).length,1) for p in stem)
print("stem pieces:", len(stem), Ls)
knot = w.select(lambda m: m.role in ("knot","knot-tail","terminal") and True).shape()
rest = w.select(lambda m: m.role not in ("knot","knot-tail","terminal")).shape()
print("knot-to-nearest-other-mark gap:", round(knot.distance(rest),2))
# expected stem length per branch
import numpy as np
pts = G.arc_pts(375,470,175,90,30,n=200)
print("full branch stem length:", round(G.Curve(pts).length,1))
