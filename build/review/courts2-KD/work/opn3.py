import sys, warnings, itertools
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np
from art import KD
from deck import courtkit as K
from shapely.geometry import LineString, Point
sc = KD.figure()
it = {i.name: i for i in sc.items}
cuff, slv = it['cuffR'].occ, it['sleeveR'].occ
def row(g, y):
    q = LineString([(420, y), (600, y)]).intersection(g)
    return None if q.is_empty else q.bounds[0]
res = []
for ex, sg in itertools.product(range(506, 545, 3), range(10, 34, 2)):
    op = K.R(K.Path((347.0, 292.0)).sag((KD.OPEN_TR, 292.0), -10.0).sag((float(ex), 545.0), float(sg)).line((259.0, 545.0)).sag((347.0, 292.0), KD.OPEN_SAG_L).close().d)
    ring = op.exterior
    pts = [ring.interpolate(t, normalized=True) for t in np.linspace(0, 1, 3000)]
    arm = cuff.union(slv)
    ins = [p for p in pts if arm.contains(p) and 380 < p.y < 520]
    if not ins: continue
    ent = min(ins, key=lambda p: p.y)
    in_cuff = cuff.contains(ent)
    # margin under the sleeve below the cuff
    m = []
    for y in range(448, 511, 3):
        xs = [p.x for p in pts if abs(p.y - y) < 0.3 and p.x > 440]
        sl = row(slv, y)
        if xs and sl is not None: m.append(min(xs) - sl)
    mm = min(m) if m else None
    res.append((ex, sg, round(ent.x,1), round(ent.y,1), in_cuff, None if mm is None else round(mm,1)))
ok = [r for r in res if r[4] and 421 <= r[3] <= 436 and r[5] is not None and r[5] >= 4.5]
for r in ok: print(r)
print(len(ok), 'current', KD.OPEN_BR, KD.OPEN_SAG, [r for r in res if r[0]==int(KD.OPEN_BR[0]) and r[1]==int(KD.OPEN_SAG)])
