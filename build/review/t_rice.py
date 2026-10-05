from rv import *
from deck.motifs import *
import numpy as np, math
from inkkit import geom as G
s = rice_stalk(0, 200, -90, 190)
print({k:(v if not isinstance(v,list) else len(v)) for k,v in s.meta.items()})
save(s, "rice_stalk_zoom", zoom=5)
# measure spikelet axes vs stalk: female should be ±15 from up (-90), male ±150
for m in s.marks:
    if m.role=="spikelet":
        pts = G.flatten(m.d,0.05)[0][0]
        # tips: farthest pair
        from scipy.spatial.distance import pdist, squareform
        D = squareform(pdist(pts)); i,j = np.unravel_index(D.argmax(), D.shape)
        a,b = pts[i], pts[j]
        L = D[i,j]
        # width: max distance from chord
        u=(b-a)/L; n=np.array([-u[1],u[0]]); wdt = (pts-a)@n; 
        ang = math.degrees(math.atan2(*(b-a)[::-1]))
print("done")
