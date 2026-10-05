from rv import *
from deck.motifs import *
from inkkit import geom as G
import shapely, numpy as np
def ref_area(f):
    return shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05) for m in f.marks]).area
def check(f, label):
    a = f.shape().area; r = ref_area(f)
    bad = abs(a-r) > 0.02*r
    if bad: print("BAD", label, round(a,1), round(r,1))
    return bad
nb=0; n=0
for fc in (1,-1):
    for rot in range(0, 360, 5):
        n+=1
        nb += check(fountain_darter(0,0,100,facing=fc,rot=rot), f"darter100 fc{fc} rot{rot}")
print("darter100 bad", nb, "of", n)
