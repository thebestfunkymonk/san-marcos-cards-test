import sys; sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import box, LineString, Point
from deck import courtkit as K
import importlib
QH = importlib.import_module('art.QH')
sc = QH.figure()
it = {i.name: i for i in sc.items}
for nm in ('armletL', 'armletR', 'collar0', 'collar1', 'neck', 'torso', 'hairF'):
    o = it[nm].occ
    print(nm, [round(v, 1) for v in o.bounds])
    if nm.startswith(('armlet', 'collar')):
        for g in K._polys_of(o):
            c = g.centroid; print('   disc', round(c.x, 2), round(c.y, 2), 'd', round(2 * (g.area / np.pi) ** .5, 2))
neck = it['neck'].occ
for y in (280, 285, 290, 295, 298, 299, 300):
    g = neck.intersection(box(0, y - 0.01, 750, y + 0.01))
    print('neck y', y, [round(v, 1) for v in g.bounds] if not g.is_empty else None)
