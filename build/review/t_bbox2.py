from rv import *
from deck.motifs import *
from inkkit import geom as G
import pathops
d2 = fountain_darter(0,0,60, facing=-1, rot=33)
save(d2, "darter60_rot_line", view=(-35,-35,35,30), zoom=6)
save(d2, "darter60_rot_ko", view=(-35,-35,35,30), zoom=6, flood=T.JADE)
# find which mark breaks the union
acc = pathops.Path(fillType=pathops.FillType.WINDING)
for i,m in enumerate(d2.marks):
    acc2 = pathops.Path(fillType=pathops.FillType.WINDING)
    acc2.addPath(acc); acc2.addPath(m.skia())
    try:
        acc2.simplify(fix_winding=True)
    except Exception as e:
        print("simplify error at", i, m.role, e); 
    b = G.bbox(G.from_skia(acc2)) if G.from_skia(acc2) else None
    print(i, m.role, b)
    acc = acc2
# other variants
for L in (60, 80, 100, 120):
    for rot in (0, 33, 90, 145):
        for fc in (1,-1):
            d = fountain_darter(0,0,L,facing=fc,rot=rot)
            import numpy as np
            bb=np.array([G.bbox(G.from_skia(m.skia())) for m in d.marks])
            full=(bb[:,0].min(), bb[:,1].min(), bb[:,2].max(), bb[:,3].max())
            ob=d.bbox()
            if max(abs(a-b) for a,b in zip(full,ob))>0.5:
                print("MISMATCH", L, rot, fc, [round(v,1) for v in ob], [round(v,1) for v in full])
