import sys, warnings
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np
from art import KD
from deck import courtkit as K
from shapely.geometry import LineString
import importlib
sc = KD.figure()
it = {i.name: i for i in sc.items}
cuff = it['cuffR'].occ
cb = np.array(cuff.exterior.coords)
print('cuffR corners approx', cb[np.argmin(cb[:,0]+cb[:,1])], cb[np.argmin(cb[:,0]-cb[:,1])])
for sg in (16, 17, 18, 19, 20, 21, 23):
    op = K.R(K.Path((347.0, 292.0)).sag((KD.OPEN_TR, 292.0), -10.0).sag((493.0, 545.0), sg).line((259.0, 545.0)).sag((347.0, 292.0), KD.OPEN_SAG_L).close().d)
    edge = op.exterior
    x = edge.intersection(cuff.exterior)
    pts = [p.coords[0] for p in getattr(x, 'geoms', [x])] if not x.is_empty else []
    print(sg, [tuple(np.round(p,1)) for p in pts])
for sg in (17, 19, 21, 23):
    op = K.R(K.Path((347.0, 292.0)).sag((KD.OPEN_TR, 292.0), -10.0).sag((493.0, 545.0), sg).line((259.0, 545.0)).sag((347.0, 292.0), KD.OPEN_SAG_L).close().d)
    row = []
    for y in (400, 410, 420, 430, 440, 450):
        q = LineString([(420, y), (560, y)]).intersection(op.exterior)
        row.append((y, np.round([p.x for p in getattr(q, 'geoms', [q])], 1).tolist() if not q.is_empty else None))
    print(sg, row)
print('crossings with the cuff/sleeve union')
arm = it['cuffR'].occ.union(it['sleeveR'].occ)
for sg in (26, 28, 29, 30, 31, 32):
    op = K.R(K.Path((347.0, 292.0)).sag((KD.OPEN_TR, 292.0), -10.0).sag((493.0, 545.0), sg).line((259.0, 545.0)).sag((347.0, 292.0), KD.OPEN_SAG_L).close().d)
    # first point along the right edge (top to bottom) inside the arm
    ring = op.exterior
    pts = [ring.interpolate(t, normalized=True) for t in np.linspace(0, 1, 4000)]
    hit = [p for p in pts if arm.contains(p) and p.y < 500]
    hit = min(hit, key=lambda p: p.y) if hit else None
    print(sg, None if hit is None else (round(hit.x,1), round(hit.y,1)), 'in cuff' if hit is not None and it['cuffR'].occ.contains(hit) else '')
