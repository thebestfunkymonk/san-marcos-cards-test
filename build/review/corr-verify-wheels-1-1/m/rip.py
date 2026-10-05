import numpy as np
from shapely.geometry import LineString
from inkkit import geom as G
from art import _back_frame as BF
f = BF.corner_ripples()
rows=[]
for m in f.marks:
    for p,_ in G.flatten(m.d,0.05):
        P=np.asarray(p)
        if P[:,0].max()<375 and P[:,1].max()<525:
            L=LineString(P)
            r=np.hypot(P[:,0]-BF.ROUNDEL_C[0],P[:,1]-BF.ROUNDEL_C[1]).mean()
            rows.append((round(r,1), round(L.length,1), tuple(np.round(P[0],1)), tuple(np.round(P[-1],1))))
for r in sorted(rows): print(r)
print('n', len(rows))
s=BF.side_band_upper(); ys=sorted({round(float(np.asarray(p)[:,1].mean()),1) for m in s.marks for p,_ in G.flatten(m.d,0.05)})
print('ladder top rungs', ys[:3])
b=BF.top_band(); print('waves', b.meta.get('n_waves'))
xs=[np.asarray(p)[:,0].min() for m in b.marks for p,_ in G.flatten(m.d,0.05)]
print('band min x', round(min(xs),2))
