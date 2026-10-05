from rv import *
from deck.motifs import *
from inkkit import geom as G
import shapely, numpy as np, pathops
def ref(f): return shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05) for m in f.marks])
def flat_union(f):
    acc = pathops.Path(fillType=pathops.FillType.WINDING)
    for m in f.marks:
        s = G.to_shape(G.from_skia(m.skia()), tol=0.02)   # flatten to polygon
        acc.addPath(G.to_skia(G.from_shape(s)))
    acc.simplify(fix_winding=True)
    return G.from_skia(acc)
nb=0;n=0
for fc in (1,-1):
    for rot in range(0,360,5):
        f=fountain_darter(0,0,100,facing=fc,rot=rot); r=ref(f).area; n+=1
        a=G.to_shape(flat_union(f),tol=0.05).area
        nb+= abs(a-r)>0.02*r
print("flattened-pathops bad", nb, "of", n)
