import sys; sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import box, LineString, Point
from deck import courtkit as K
import importlib
QH = importlib.import_module('art.QH')
nm = sys.argv[1]; bb = tuple(map(float, sys.argv[2:6]))
sc = QH.figure()
Z = box(*bb)
for it in sc.items:
    if it.name != nm: continue
    for m in it.frag.marks:
        if m.kind == 'fill' or not m.d: continue
        for pts, _ in K.G.flatten(m.d, 0.2):
            if len(pts) < 2: continue
            ln = LineString(pts)
            if ln.intersects(Z):
                g = ln.intersection(Z)
                for s in K._lines_of(g):
                    c = np.asarray(s.coords)
                    print(m.role, getattr(m, 'width', None), 'len', round(s.length, 1), 'from', np.round(c[0], 1), 'to', np.round(c[-1], 1))
