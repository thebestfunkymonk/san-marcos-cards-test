import sys, warnings
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import importlib.util, numpy as np
from shapely.geometry import LineString
spec = importlib.util.spec_from_file_location('kdk', 'art/KD.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
it = {i.name: i for i in sc.items}
def region(g, cx, cy, r=8, W=1.0):
    ring = LineString(g.exterior.coords); L = ring.length
    def P(s): return np.array(ring.interpolate(s % L).coords[0])
    for s in np.arange(0, L, 0.4):
        p = P(s)
        if np.hypot(p[0]-cx, p[1]-cy) > r: continue
        v1, v2 = p - P(s-W), P(s+W) - p
        t = np.degrees(np.arctan2(v1[0]*v2[1]-v1[1]*v2[0], v1@v2))
        if abs(t) > 4: print(f'   ({p[0]:.1f},{p[1]:.1f}) {t:6.1f}')
nm, cx, cy = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
region(it[nm].occ, cx, cy, float(sys.argv[4]) if len(sys.argv) > 4 else 8)
