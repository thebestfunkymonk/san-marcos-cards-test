import sys
sys.path.insert(0, "art")
import numpy as np
from shapely.geometry import Point
import QC
from deck import courtkit as K
import _qc_gown as GW
extra = eval(sys.argv[1]) if len(sys.argv) > 1 else {}
QC.PACK = dict(QC.PACK, **extra)
cap = {}
orig = GW.leaf_pack
def spy(allowed, **kw):
    f, placed = orig(allowed, **kw); cap['placed'] = placed; cap['kw'] = kw; return f, placed
GW.leaf_pack = spy
sc, fc = QC.figure()
it = {i.name: i for i in sc.items}
for (b, L, W, bd, pg) in cap['placed']:
    sp = GW._spikes(b, cap['kw']['heading'], L, bd)
    print([round(v) for v in b], L, round(W,1), "vis frac", round(pg.difference(K.R(cap['kw']['soft'])).area / pg.area, 2),
          "spike depth in sleeveR", [round(it['sleeveR'].occ.exterior.distance(Point(*q)) * (1 if it['sleeveR'].occ.contains(Point(*q)) else -1), 1) for q in sp])
