import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'art'))
import numpy as np, shapely
from shapely.geometry import LineString, box
import QC
from inkkit import geom as G
def has_lower(fr):
    pr = box(513, 234.5, 517, 237.5)
    n=0
    for m in fr.marks:
        if m.kind!='stroke' or not m.d or m.role!='outline': continue
        for pts, closed in G.as_polys(m.d, 0.05):
            pts=np.asarray(pts,float)
            if len(pts)<2: continue
            ln = LineString(pts) if not closed else shapely.LinearRing(pts)
            if ln.intersects(pr): n+=1
    return n
sc,_=QC.figure(); print('current', has_lower(QC.compose_scene(sc)))
QC.SCEPTRE = dict(QC.SCEPTRE); QC.SCEPTRE.pop('knop_ink')
sc,_=QC.figure(); print('no knop_ink', has_lower(QC.compose_scene(sc)))
