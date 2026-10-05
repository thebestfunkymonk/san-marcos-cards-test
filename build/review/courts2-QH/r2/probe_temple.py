import sys; sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import box, LineString, Point
from deck import courtkit as K
import importlib
QH = importlib.import_module('art.QH')
sc = QH.figure()
it = {i.name: i for i in sc.items}
for nm in ('hairF', 'head', 'rim', 'neck'):
    o = it[nm].occ
    print(nm, [round(v, 1) for v in o.bounds])
head = it['head'].occ
hf = it['hairF'].occ
rim = it['rim'].occ
# face contour x at y
for y in range(170, 232, 4):
    ln = LineString([(380, y), (470, y)])
    hx = head.boundary.intersection(ln)
    fx = hf.intersection(ln)
    rx = rim.intersection(ln)
    print(y, 'head', [round(p.x, 1) for p in getattr(hx, 'geoms', [hx]) if not p.is_empty],
          'hairF', [round(v, 1) for v in fx.bounds] if not fx.is_empty else None,
          'rim', [round(v, 1) for v in rx.bounds] if not rx.is_empty else None)
print('rim coords right end', [ (round(x,1), round(y,1)) for x, y in rim.exterior.coords if x > 410])
