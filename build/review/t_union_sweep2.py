from rv import *
from deck.motifs import *
from deck.motifs import sheet_figurative as SF
from inkkit import geom as G
import shapely, numpy as np, time
def ref(f): return shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05) for m in f.marks if m.d]).area
def bad(f):
    a=f.shape().area; r=ref(f); return abs(a-r)>0.01*r, a, r
for sp in SF.specimens():
    b,a,r = bad(sp["frag"])
    print(("BAD " if b else "ok  ")+sp["title"], round(a,1), round(r,1))
# back orbit darters
import math
for ang in (-60, -58, -62):
    x=375+175*math.cos(math.radians(ang)); y=525+175*math.sin(math.radians(ang))
    d=fountain_darter(x,y,100,rot=ang+90); pair = d + d.rot180()
    print("orbit", ang, bad(pair))
