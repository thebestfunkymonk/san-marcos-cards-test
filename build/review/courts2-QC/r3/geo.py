import sys, os
sys.path.insert(0, "art")
import QC
from deck import courtkit as K
import numpy as np
sc, fc = QC.figure()
it = {i.name: i for i in sc.items}
print([i.name for i in sc.items])
for nm in ("cuffR", "sleeveR", "handR", "culm", "handR~heel~culm", "handR~culm"):
    if nm in it and it[nm].occ is not None:
        g = it[nm].occ
        print(nm, [round(v,1) for v in g.bounds], "halo", it[nm].halo)
cf = it["cuffR"].occ
print("cuff coords", [tuple(round(c,1) for c in p) for p in list(cf.exterior.coords)[::4]])
WR = K.fist_wrist(QC.FIST_R, -90.0, bend=45.0, shaft_w=19.0, back=-1, h=34.0)
print("WR", WR)
h = it["handR"].occ
ys = np.arange(430, 480, 2.0)
import shapely
for y in ys:
    ln = shapely.LineString([(480, y), (560, y)])
    for nm in ("handR", "cuffR", "sleeveR"):
        x = it[nm].occ.intersection(ln)
        if not x.is_empty:
            print(y, nm, [round(v,1) for v in x.bounds])
