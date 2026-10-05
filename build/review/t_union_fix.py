from rv import *
from deck.motifs import *
from inkkit import geom as G
import shapely, numpy as np, pathops
def ref_area(f):
    return shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05) for m in f.marks]).area
def alt_outline(f):
    paths=[m.skia() for m in f.marks if m.d]
    # balanced pairwise union with PathOp.UNION
    while len(paths)>1:
        nxt=[]
        for i in range(0,len(paths),2):
            if i+1<len(paths):
                nxt.append(pathops.op(paths[i], paths[i+1], pathops.PathOp.UNION, fix_winding=True))
            else: nxt.append(paths[i])
        paths=nxt
    return G.from_skia(paths[0])
def alt2(f):
    paths=[m.skia() for m in f.marks if m.d]
    res = pathops.Path()
    b = pathops.OpBuilder(fix_winding=True)
    for p in paths: b.add(p, pathops.PathOp.UNION)
    return G.from_skia(b.resolve())
nb1=nb2=0; n=0
for fc in (1,-1):
    for rot in range(0,360,5):
        f=fountain_darter(0,0,100,facing=fc,rot=rot); r=ref_area(f); n+=1
        a1=G.to_shape(alt_outline(f),tol=0.05).area; a2=G.to_shape(alt2(f),tol=0.05).area
        nb1 += abs(a1-r)>0.02*r; nb2 += abs(a2-r)>0.02*r
print("pairwise op bad", nb1, "opbuilder bad", nb2, "of", n)
