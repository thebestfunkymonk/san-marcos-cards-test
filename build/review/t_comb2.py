from rv import *
from deck.motifs import *
from inkkit import geom as G
import shapely, numpy as np
def ref(f): return shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05) for m in f.marks if m.d]).area
base = comb_spray("M0 0 L0 -130", cone=11)
shown=0
for rot in range(0,360,4):
    f = Frag(base.rotate(rot).translate(375,525).marks)
    a=f.shape().area; r=ref(f)
    if abs(a-r)>0.02*r:
        print("bad rot", rot, round(a,1), round(r,1))
        if shown<1:
            save(f, f"comb_bad_rot{rot}_ko", zoom=5, flood=T.JADE, pad=10); save(f, f"comb_bad_rot{rot}_line", zoom=5, pad=10); shown+=1
