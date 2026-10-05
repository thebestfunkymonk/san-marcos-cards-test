import numpy as np
from inkkit import geom as G
from tuck import _tuck_front as TF
def ends():
    rows=set()
    for m in TF.frame_rules().marks:
        for p,_ in G.flatten(m.d, 0.05):
            P=np.asarray(p)
            if len(P)<2: continue
            for e in (P[0],P[-1]):
                if e[0]<200 and e[1]<200: rows.add((m.w, round(float(e[0]),2), round(float(e[1]),2)))
    lad = TF.side_ladders()
    ys = sorted({round(float(np.asarray(p)[:,1].min()),2) for m in lad.marks for p,_ in G.flatten(m.d,0.05) if np.asarray(p)[:,0].max()<100 and np.asarray(p)[:,1].min()<300})
    return sorted(rows), ys[:3]
print('after', TF.ROUNDEL_C, ends())
TF.ROUNDEL_C=(53.0,59.0)
print('before', TF.ROUNDEL_C, ends())
