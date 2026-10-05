import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'art'))
import numpy as np, shapely
from shapely.geometry import LineString, box
import QC
from inkkit import geom as G
sc,_=QC.figure(); fr=QC.compose_scene(sc)
for pr,lab in ((box(541,238,550,250),'Rjunction'),(box(532,238,541,250),'Ljunction')):
  for m in fr.marks:
    if not m.d or m.layer!='ink': continue
    for pts, closed in G.as_polys(m.d, 0.05):
        pts=np.asarray(pts,float)
        if len(pts)<2: continue
        ln = LineString(pts) if not closed else shapely.LinearRing(pts)
        if ln.intersects(pr):
            print(lab, m.kind, m.role, m.w, round(ln.length,2), [round(b,1) for b in ln.bounds])
