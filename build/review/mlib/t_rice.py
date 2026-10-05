from rh import *
import math, numpy as np
from deck.motifs import rice as RI
from inkkit import geom as G
f = RI.rice_stalk(0, 0, -90, 190)
show(f, "stalk190-5x", zoom=5)
# measure spikelet geometry
sp = [m for m in f.marks if m.role=="spikelet"]
ped = [m for m in f.marks if m.role=="pedicel"]
awn = [m for m in f.marks if m.role=="awn"]
print("spikelets", len(sp), "pedicels", len(ped), "awns", len(awn), "female", len(f.meta['female']), "male", len(f.meta['male']))
for m in ped[:3]:
    p = G.flatten(m.d)[0][0]; print(" pedicel len", round(G.Curve(p).length,2), "angle from stalk(up)", round(math.degrees(math.atan2(p[-1][0]-p[0][0], -(p[-1][1]-p[0][1]))),1))
for m in sp[:3] + sp[-3:]:
    x0,y0,x1,y1 = G.bbox(m.d)
    pts = G.flatten(m.d)[0][0]
    # vesica axis: farthest pair
    D = np.hypot(*(pts[:,None,:]-pts[None,:,:]).transpose(2,0,1))
    i,j = np.unravel_index(np.argmax(D), D.shape)
    a,b = pts[i], pts[j]
    ang = math.degrees(math.atan2(b[0]-a[0], -(b[1]-a[1])))
    print(" spikelet len", round(D[i,j],2), "axis angle from vertical", round(ang,1))
print("f_pitch", round(f.meta['f_pitch'],2), "m_pitch", round(f.meta['m_pitch'],2))
w = RI.rice_wreath_arc(0, 0, 150, leaf_len=64, ratio=10.0)
print("wreath warnings", w.meta.get('warnings'))
