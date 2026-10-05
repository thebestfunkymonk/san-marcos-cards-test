import sys; sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import box, LineString, Point
from deck import courtkit as K
import importlib
QH = importlib.import_module('art.QH')
from art import _qh_tidy as TD
sc = QH.figure()
it = {i.name: i for i in sc.items}
slR = it['sleeveR']
sil = sc.silhouette()
for y in range(360, 412, 3):
    ln = LineString([(556, y), (620, y)])
    g = sil.boundary.intersection(ln)
    xs = sorted(p.x for p in getattr(g, 'geoms', [g]) if not p.is_empty)
    # seam: find lines with role seam in sleeveR frag
    sx = []
    for m in slR.frag.marks:
        if m.role != 'seam' or not m.d: continue
        for pts, _ in K.G.flatten(m.d, 0.05):
            if len(pts) < 2: continue
            gg = LineString(pts).intersection(ln)
            if not gg.is_empty: sx += [p.x for p in getattr(gg, 'geoms', [gg])]
    print(y, 'sil', [round(x, 1) for x in xs], 'seam', [round(x, 1) for x in sorted(sx)])
for m in slR.frag.marks:
    if m.kind != 'fill': print(m.role, getattr(m, 'w', None))
