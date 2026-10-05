from rv import *
from deck.motifs import *
from inkkit import geom as G
import shapely, numpy as np, pathops
from shapely.geometry import LineString
def shp_mark(m):
    if m.kind=="fill": return G.to_shape(m.d, tol=0.02)
    geoms=[]
    for pts,closed in G.flatten(m.d,0.01):
        if len(pts)<2: continue
        ln = LineString(np.vstack([pts,pts[:1]]) if closed else pts)
        cap = "round" if m.cap=="round" else "flat"
        geoms.append(ln.buffer(m.w/2, cap_style=cap, join_style="round" if m.join=="round" else "mitre", mitre_limit=m.miter))
    return shapely.union_all(geoms)
from collections import Counter
cnt=Counter()
for fc in (1,-1):
    for rot in range(0,360,5):
        f=fountain_darter(0,0,100,facing=fc,rot=rot)
        for m in f.marks:
            a=G.to_shape(G.from_skia(m.skia()),tol=0.02).area
            r=shp_mark(m).area
            if abs(a-r)>0.03*r+0.5:
                cnt[m.role]+=1
                if cnt[m.role]<=2: print(fc,rot,m.role, round(a,1), round(r,1))
print(cnt)
