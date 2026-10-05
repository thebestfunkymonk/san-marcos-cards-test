import sys, warnings; sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np, shapely
from shapely.geometry import LineString, Point
import art.KH as KH
from art import _kh_parts as KP
from deck import courtkit as K
from inkkit import geom as G
cap = {}
orig = KP.ring_clear
def spy(rip, front, **kw):
    cap['rip'] = rip; cap['front'] = front; cap['kw'] = kw
    out = orig(rip, front, **kw); cap['out'] = out; return out
KP.ring_clear = spy
sc = KH.figure()
q = Point(float(sys.argv[1]), float(sys.argv[2]))
front = K.R(cap['front'])
for tag in ('rip', 'out'):
    for i, m in enumerate(cap[tag].marks):
        for p, closed in G.flatten(m.d, 0.1):
            pts = np.vstack([p, p[:1]]) if closed else np.asarray(p)
            ln = LineString(pts)
            if ln.distance(q) < 6:
                vis = ln.difference(front.buffer(-0.3))
                print(tag, i, 'len', round(ln.length,1), 'd', round(ln.distance(q),2), 'vis', round(vis.length,1), np.round(pts[0],1), np.round(pts[-1],1))
m = cap['rip'].marks[11]
for p, closed in G.flatten(m.d, 0.1):
    ln = LineString(np.asarray(p))
    fz = front.buffer(7.3); fin = front.buffer(-0.3)
    vis = ln.difference(fin)
    nearv = vis.intersection(fz)
    print('vis', round(vis.length,1), 'nearv', round(nearv.length,1), 'end->front', round(Point(*p[-1]).distance(front),2), 'start->front', round(Point(*p[0]).distance(front),2))
    for comp in K._lines_of(shapely.line_merge(nearv)):
        print('  comp', round(comp.length,1), 'touch', round(comp.distance(front),2), np.round(comp.coords[0],1), np.round(comp.coords[-1],1))
