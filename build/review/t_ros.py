from rv import *
from deck.motifs import *
from inkkit import geom as G
import numpy as np, math
r = source_rosette(375,525,130)
sp = r.meta["rosette"]; print({k:v for k,v in sp.items()})
from collections import Counter
print(Counter((m.role, m.w, m.cap) for m in r.marks))
# ring radii
for m in r.marks:
    if m.role in ("ring","rule"):
        x0,y0,x1,y1=G.bbox(m.d); print(m.role, round((x1-x0)/2,2))
# hatch pitch in one cell
h=[m for m in r.marks if m.role=="hatch"]
print("hatch marks", len(h))
pts=[p for p,c in G.flatten(h[0].d,0.01)]
print("lines in first hatch mark", len(pts))
mids=[ (p[0]+p[-1])/2 for p in pts]
dirs=[ (p[-1]-p[0])/np.hypot(*(p[-1]-p[0])) for p in pts]
n=np.array([-dirs[0][1],dirs[0][0]])
proj=sorted(float(m@n) for m in mids); print("pitch", np.round(np.diff(proj),2))
# wave hooks
print("wave meta", r.meta.get("n_waves"), r.meta.get("wave_height"), r.meta.get("wave_rmax"))
d=G.bbox(r.outline()); print("rosette outer bbox radius", (d[2]-d[0])/2)
