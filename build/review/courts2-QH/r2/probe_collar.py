import sys; sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import box, LineString, Point
from deck import courtkit as K
import importlib
QH = importlib.import_module('art.QH')
sc = QH.figure()
it = {i.name: i for i in sc.items}
for nm in ('collar0', 'collar1'):
    print(nm)
    for g in it[nm].occ.geoms if hasattr(it[nm].occ, 'geoms') else [it[nm].occ]:
        print('  ', [round(v, 1) for v in g.bounds])
neck, torso, hf = it['neck'].occ, it['torso'].occ, it['hairF'].occ
for x in (360, 365, 368, 372, 395, 400, 403, 406, 409):
    l = LineString([(x, 270), (x, 320)])
    print('x', x, 'neck', [round(v, 1) for v in neck.intersection(l).bounds] if not neck.intersection(l).is_empty else None,
          'torso', [round(v, 1) for v in torso.intersection(l).bounds] if not torso.intersection(l).is_empty else None,
          'torso-hairF', [round(v, 1) for v in torso.difference(hf).intersection(l).bounds] if not torso.difference(hf).intersection(l).is_empty else None)
