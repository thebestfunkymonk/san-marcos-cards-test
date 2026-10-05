from rv import *
from deck.motifs import *
from inkkit import geom as G
d2 = fountain_darter(0,0,60, facing=-1, rot=33)
print("bbox", d2.bbox())
o = d2.outline()
print(len(o))
# per-mark bbox union
import numpy as np
bb=[]
for m in d2.marks:
    b = G.bbox(G.from_skia(m.skia()))
    bb.append(b)
bb=np.array(bb); print("per-mark union", bb[:,0].min(), bb[:,1].min(), bb[:,2].max(), bb[:,3].max())
print(d2.shape().bounds)
