"""redprobe.py [module] y0 y1 x0 x1 — per-layer fill spans along rows (composed scene)."""
import sys, os, importlib.util, warnings
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art"); warnings.simplefilter("ignore")
from shapely.geometry import LineString
from deck import courtkit as K
from inkkit import geom as G
path = sys.argv[1]
spec = importlib.util.spec_from_file_location("qdmod", path); m = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.dirname(os.path.abspath(path))); spec.loader.exec_module(m)
sc = m.figure(); res = m.compose_scene(sc)
y0, y1, x0, x1 = map(float, sys.argv[2:6])
lay = {}
for mk in res.marks:
    if mk.kind == "fill":
        lay.setdefault(mk.layer, []).append(G.to_shape(mk.d, tol=0.05))
    else:
        lay.setdefault("ink-stroke", []).append(G.to_shape(mk.d, tol=0.05).buffer(mk.w / 2, cap_style=1))
U = {k: K.U(*v) for k, v in lay.items()}
import numpy as np
for y in np.arange(y0, y1 + 0.01, (y1 - y0) / 8 or 1):
    ln = LineString([(x0, y), (x1, y)])
    row = []
    for k, g in U.items():
        for s in K._lines_of(ln.intersection(g)):
            row.append((round(s.bounds[0], 1), round(s.bounds[2], 1), k))
    print(round(y, 1), sorted(row))
