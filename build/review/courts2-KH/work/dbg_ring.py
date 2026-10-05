import sys, warnings; sys.path.insert(0,'.'); sys.path.insert(0,'build/review/courts2-KH/work'); warnings.simplefilter('ignore')
import numpy as np, shapely
from shapely.geometry import LineString, Point
import art.KH as KH
from art import _kh_parts as KP
from deck import courtkit as K
from inkkit import geom as G
from armR import setR, setL
setR(KH,K,55,0.85); KH.HEEL_FIX=('L','R'); setL(KH,K,35,0.95,width=48)
# capture rip and front by monkeypatching ring_clear
cap = {}
orig = KP.ring_clear
def spy(rip, front, **kw):
    cap['rip'] = rip; cap['front'] = front
    return orig(rip, front, **kw)
KP.ring_clear = spy
KH.RING_CLEAR = True
sc = KH.figure()
rip, front = cap['rip'], K.R(cap['front'])
q = Point(259, 432)
fz = front.buffer(7.3); fin = front.buffer(-0.3)
for i, m in enumerate(rip.marks):
    for p, closed in G.flatten(m.d, 0.1):
        pts = np.vstack([p, p[:1]]) if closed else np.asarray(p)
        ln = LineString(pts)
        if ln.distance(q) < 12:
            vis = ln.difference(fin)
            print(i, 'len', round(ln.length,1), 'dist', round(ln.distance(q),2), 'vis', round(vis.length,1))
            for comp in K._lines_of(shapely.line_merge(vis.intersection(fz))):
                print('   comp', round(comp.length,2), 'touch', round(comp.distance(front),2), np.round(comp.coords[0],1), np.round(comp.coords[-1],1))
