import sys, itertools
sys.path.insert(0, "art")
import numpy as np
import QC
from deck import courtkit as K
import _qc_gown as GW
cap = {}
orig_pack = GW.leaf_pack
def spy(allowed, **kw):
    cap['allowed'] = allowed; cap['kw'] = kw
    return orig_pack(allowed, **kw)
GW.leaf_pack = spy
sc, fc = QC.figure()
allowed, kw = cap['allowed'], dict(cap['kw'])
left = K.box(150, 300, 356, 560)
al = allowed.intersection(left)
res = []
for ox, oy in itertools.product(np.arange(0, 12, 1.0), np.arange(0, 12, 1.0)):
    k2 = dict(kw); k2['origin'] = (375.0 + ox, 330.0 + oy); k2['grid'] = 2.0
    for lengths in ((125.0, 110.0, 100.0), (110.0, 100.0, 90.0)):
        k2['lengths'] = lengths
        f, placed = orig_pack(al, **k2)
        if placed:
            res.append((len(placed), ox, oy, lengths, [(tuple(round(v) for v in pg.bounds), L) for (b, L, W, bd, pg) in placed]))
res.sort(key=lambda r: -r[0])
for r in res[:40]:
    print(r)
print(len(res))
