"""healdbg.py <module> x0 y0 x1 y1 — run the real compose; for heal todo entries whose victim lies in the box,
print victim roles/layer and the neighbour piece's layer/bounds."""
import sys, warnings
sys.path.insert(0, '.')
warnings.simplefilter('ignore')
import importlib.util
import shapely
from shapely.geometry import box
from deck import courtkit as K
spec = importlib.util.spec_from_file_location('kdh', sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
bx = box(*map(float, sys.argv[2:6]))
orig_dist = K.heal
import numpy as np
# wrap _run_len? simpler: monkeypatch STRtree query results by wrapping heal's note via replace of shapely.STRtree
orig_tree = shapely.STRtree
class T2(orig_tree):
    def __init__(self, geoms, *a, **k):
        super().__init__(geoms, *a, **k); self._g = geoms
    def query(self, geoms, predicate=None, distance=None):
        r = super().query(geoms, predicate=predicate, distance=distance)
        if distance is not None:
            for a, b in zip(*r):
                if a < b:
                    ga, gb = self._g[a], self._g[b]
                    d = ga.distance(gb)
                    if 0.08 <= d < 4.2 and (ga.intersects(bx) or gb.intersects(bx)):
                        print(f"pair d={d:.2f}  A bounds={tuple(round(v,1) for v in ga.bounds)} area={ga.area:.1f} | B bounds={tuple(round(v,1) for v in gb.bounds)} area={gb.area:.1f}")
        return r
shapely.STRtree = T2
sc = m.figure()
res = sc.compose()
