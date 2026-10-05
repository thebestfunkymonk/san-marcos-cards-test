import sys; sys.path.insert(0,'.')
import numpy as np
from shapely.geometry import LineString, Point
from deck import courtkit as K
from art import KC
sc = KC.figure({})
it = {i.name: i for i in sc.items}
cuff = it['cuffR'].occ; slv = it['sleeveR'].occ
both = K.U(cuff, slv)
# corners of the cuff polygon near the left edge
cc = np.asarray(cuff.exterior.coords)
print('cuff pts (x<495):', [tuple(np.round(p,1)) for p in cc if p[0] < 495 and p[1] < 450][:20])
def rx(X,y): return 375 + X*(y+400)/911
for X in np.arange(100, 121, 1.0):
    ln = LineString([(rx(X,300),300),(rx(X,520),520)])
    h = ln.intersection(both.boundary)
    pts = [np.asarray(g.coords[0]) for g in getattr(h,'geoms',[h])] if not h.is_empty else []
    if not pts: print(X, None); continue
    p = min(pts, key=lambda q: q[1])
    dc = min(np.hypot(*(cc[:, :2] - p).T))
    print(X, np.round(p,1), 'on cuff' if cuff.boundary.distance(Point(*p))<0.3 else 'on sleeve', 'dist to nearest cuff vertex %.1f' % dc)
print('--- clearance of the visible ray to the cuff')
for X in np.arange(104, 113, 1.0):
    ln = LineString([(rx(X,300),300),(rx(X,520),520)])
    vis = ln.difference(both)
    pcs = [g for g in getattr(vis,'geoms',[vis]) if g.bounds[1] < 440]
    top = max(pcs, key=lambda g: g.length)
    print(X, 'min dist to cuff %.2f' % top.distance(cuff), ' land', np.round(np.asarray(top.coords[-1]),1))
