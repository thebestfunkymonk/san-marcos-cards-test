from rh import *
import numpy as np, math
from inkkit import geom as G
from shapely.geometry import Point, LineString
# A) ring over ring (two crossings), B) ring under a hatched lozenge, C) three strands
r1 = C.stroke(G.circle_d(0, 0, 30)); r2 = C.stroke(G.circle_d(35, 0, 30))
A = C.interlace(r2, r1)
print("A: under pieces", len(G.flatten(A.marks[0].d)), "clear", round(C.Frag([A.marks[0]]).shape().distance(r1.shape()), 3))
loz = C.stroke(C.lozenge_d(110, 0, 60, 30), style="point") + C.half_hatch(C.lozenge_d(110, 0, 60, 30), [(80, 0), (140, 0)], "perp", side=1)
wave = C.stroke("M70 20 C 90 -30 130 30 150 -20", T.MEDIUM)
B = C.interlace(wave, loz)
print("B: wave pieces", len(G.flatten(B.select(lambda m: m.w == T.MEDIUM).marks[0].d)),
      "clear to lozenge+hatch", round(B.select(lambda m: m.w == T.MEDIUM).shape().distance(loz.shape()), 3))
# C) plait: s1 over s2, s2 over s3, s3 over s1 (cyclic) via successive cuts
s1 = C.stroke("M180 -30 L260 30"); s2 = C.stroke("M180 30 L260 -30"); s3 = C.stroke("M220 -40 L220 40")
c1 = C.cut(s2, s1); c3 = C.cut(s3, c1)
Cf = s1 + c1 + c3
show(A + B + Cf, "interlace-6x", zoom=6)
# D) half_hatch on an S-split crescent and an annulus
cres = G.from_shape(Point(0, 0).buffer(40).difference(Point(12, 0).buffer(34)))
ann = G.from_shape(Point(0, 0).buffer(40).difference(Point(0, 0).buffer(22)))
S = "M0 -45 C 20 -20 -20 20 0 45"
h1 = C.half_hatch(cres, S, "perp", side=1) + C.stroke(cres) + C.stroke(S)
h2 = (C.half_hatch(ann, "left", C.DIAG) + C.stroke(ann) + C.stroke("M0 -40L0 40")).translate(100, 0)
show(h1 + h2, "halfhatch-6x", zoom=6)
# ends on centrelines?
def free_ends(h, lines):
    ml = [LineString(p) for m in lines.marks for p, _ in G.flatten(m.d, 0.02)]
    from shapely.ops import unary_union
    U = unary_union(ml)
    hs = [p for m in h.marks if m.role == "hatch" for p, _ in G.flatten(m.d)]
    bad = [(q.round(1), round(U.distance(Point(q)), 2)) for p in hs for q in (p[0], p[-1]) if U.distance(Point(q)) > 0.05]
    return len(hs), bad
hh = C.half_hatch(cres, S, "perp", side=1)
print("crescent S-split:", free_ends(hh, C.stroke(cres) + C.stroke(S)))
hh2 = C.half_hatch(ann, "left", C.DIAG)
print("annulus left:", free_ends(hh2, C.stroke(ann) + C.stroke("M0 -40L0 40")))
