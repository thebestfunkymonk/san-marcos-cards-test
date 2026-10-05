from rv import *
from deck.motifs import *
from inkkit import geom as G
import shapely, numpy as np
def ref(f): return shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05) for m in f.marks if m.d]).area
c = comb_spray("M375 250 L375 118", cone=11)
for f,name in ((c,"up"),(c.rot180(),"down"), (comb_spray("M375 250 L380 118", cone=11),"tilt")):
    f=Frag(f.marks); print(name, round(f.shape().area,1), round(ref(f),1))
rng = np.random.default_rng(7)
base = comb_spray("M0 0 L0 -130", cone=11)
for i in range(24):
    rot = float(rng.uniform(0,360)); tx,ty = rng.uniform(0,750), rng.uniform(0,1050)
    f = Frag(base.rotate(rot).translate(tx,ty).marks)
    a=f.shape().area; r=ref(f)
    if abs(a-r)>0.01*r:
        print("bad", i, rot, tx, ty, a, r)
        save(f, f"comb_bad_{i}_ko", zoom=4, flood=T.JADE, pad=10)
        save(f, f"comb_bad_{i}_line", zoom=4, pad=10)
