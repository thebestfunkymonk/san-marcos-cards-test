import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'art'))
import numpy as np, shapely
from shapely.geometry import LineString, box
import QC
from inkkit import geom as G
sp = QC.S.rice_sceptre(QC.SCEPTRE_X, **QC.SCEPTRE)
def strokes_in(frag, pr, label):
    for m in frag.marks:
        if not m.d: continue
        for pts, closed in G.as_polys(m.d, 0.05):
            if len(pts)<2: continue
            pts=np.asarray(pts,float)
            ln = LineString(pts) if not closed else shapely.LinearRing(pts)
            if ln.intersects(pr):
                seg = ln.intersection(pr)
                print(label, m.kind, m.role, getattr(m,'width',None), getattr(m,'layer',None), round(seg.length,2), [round(b,1) for b in seg.bounds])
pr = box(513, 226, 517, 242)
print('--- sceptre part'); strokes_in(sp.frag, pr, 'sp')
sc, _ = QC.figure()
fr = QC.compose_scene(sc)
print('--- composed'); strokes_in(fr, pr, 'c')
print([f for f in dir(sp.frag.marks[0]) if not f.startswith('_')])
