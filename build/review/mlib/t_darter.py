from rh import *
import numpy as np
from deck.motifs import fauna as FA
from inkkit import geom as G
f = FA.fountain_darter(0, 0, 100)
show(f, "darter100-8x", zoom=8)
show(f, "darter100-ko-8x", zoom=8, flood=T.JADE)
# measurements
eye = [m for m in f.marks if m.role == "eye"][0]
pup = [m for m in f.marks if m.role == "pupil"][0]
ex0,ey0,ex1,ey1 = G.bbox(eye.d); px0,py0,px1,py1 = G.bbox(pup.d)
print("eye ring centreline dia", round(ex1-ex0,2), "stroke", eye.w, "-> inner hole dia", round(ex1-ex0-eye.w,2))
print("pupil dia", round(px1-px0,2), "pupil centre", ((px0+px1)/2, (py0+py1)/2), "eye centre", ((ex0+ex1)/2,(ey0+ey1)/2))
eyeu = C.Frag([eye]).shape(); pu = C.Frag([pup]).shape()
hole = eyeu.convex_hull.difference(eyeu).difference(pu)
print("visible ground inside eye ring (px^2):", round(hole.area,3))
st = [p for m in f.marks if m.role=="stitch" for p,_ in G.flatten(m.d)]
xs = [x for p in st for x in (p[0][0], p[-1][0])]
ol = f.select(lambda m: m.role=="outline").bbox()
print("body x", round(ol[0],1), round(ol[2],1), "stitch x", round(min(xs),1), round(max(xs),1), "n dashes", len(st))
print("stitch covers fraction of body length:", round((max(xs)-min(xs))/(ol[2]-ol[0]),2))
sad = [p for m in f.marks if m.role=="saddle" for p,_ in G.flatten(m.d)]
print("saddles", len(sad), [round(p[0][0],1) for p in sad], "lens", [round(abs(p[-1][1]-p[0][1]),1) for p in sad])
print("warnings", f.meta.get("warnings"))
for L in (60, 80, 140):
    g = FA.fountain_darter(0,0,L)
    print(L, "warnings", g.meta.get("warnings"), "saddles", sum(len(G.flatten(m.d)) for m in g.marks if m.role=="saddle"))
