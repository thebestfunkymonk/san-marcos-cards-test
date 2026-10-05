import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'art'))
import numpy as np, shapely
from shapely.geometry import LineString, Point, box
import QC
from deck import courtkit as K
from inkkit import geom as G
from deck.motifs import core as C
sp = QC.S.rice_sceptre(QC.SCEPTRE_X, **QC.SCEPTRE)
probe = box(508, 238, 522, 252)   # left arm underside region
probeR = box(560, 238, 574, 252)
def strokes_in(frag, pr, label):
    n=0
    for m in frag.marks:
        if m.kind!='stroke' or not m.d: continue
        for pts, closed in G.as_polys(m.d, 0.05):
            if len(pts)<2: continue
            ln = LineString(np.asarray(pts,float)) if not closed else shapely.LinearRing(np.asarray(pts,float))
            if ln.intersects(pr):
                n+=1
                seg = ln.intersection(pr)
                print(label, m.role, m.width if hasattr(m,'width') else '', getattr(m,'layer',''), round(seg.length,2), seg.bounds)
    return n
print('--- sceptre part lines')
strokes_in(sp.frag if hasattr(sp,'frag') else sp.lines, probe, 'spL')
strokes_in(sp.frag if hasattr(sp,'frag') else sp.lines, probeR, 'spR')
sc, _ = QC.figure()
fr = QC.compose_scene(sc)
print('--- composed')
strokes_in(fr, probe, 'cL'); strokes_in(fr, probeR, 'cR')
print('heal log entries near arms:')
for e in getattr(sc,'heal_log',[]):
    s=str(e)
    print(s[:300])
