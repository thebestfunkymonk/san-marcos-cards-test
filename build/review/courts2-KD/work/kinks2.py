import sys, warnings
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import importlib.util, numpy as np
from shapely.geometry import LineString
from deck import courtkit as K
spec = importlib.util.spec_from_file_location('kdk', sys.argv[1] if len(sys.argv)>1 else 'art/KD.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
it = {i.name: i for i in sc.items}
W = float(sys.argv[2]) if len(sys.argv)>2 else 1.5
def scan(g, nm, box=None):
    ring = LineString(g.exterior.coords)
    L = ring.length
    ss = np.arange(0, L, 0.25)
    pts = np.array([ring.interpolate(s).coords[0] for s in ss])
    def P(s): return np.array(ring.interpolate(s % L).coords[0])
    out = []
    for s, p in zip(ss, pts):
        a, c = P(s - W), P(s + W)
        v1, v2 = p - a, c - p
        t = np.degrees(np.arctan2(v1[0]*v2[1]-v1[1]*v2[0], v1@v2))
        out.append((s, p, t))
    # local extrema of |t| above threshold
    res = []
    for i in range(len(out)):
        s, p, t = out[i]
        if abs(t) < 18: continue
        if abs(t) >= max(abs(out[i-1][2]), abs(out[(i+1) % len(out)][2])):
            res.append((p, t))
    print(nm)
    for p, t in res:
        print(f'   {t:6.1f} at ({p[0]:.1f},{p[1]:.1f})')
for nm in ('handL', 'handR'):
    scan(it[nm].occ, nm)
def region(g, cx, cy, r=8, W=1.0):
    ring = LineString(g.exterior.coords); L = ring.length
    def P(s): return np.array(ring.interpolate(s % L).coords[0])
    for s in np.arange(0, L, 0.5):
        p = P(s)
        if np.hypot(p[0]-cx, p[1]-cy) > r: continue
        v1, v2 = p - P(s-W), P(s+W) - p
        t = np.degrees(np.arctan2(v1[0]*v2[1]-v1[1]*v2[0], v1@v2))
        print(f'   ({p[0]:.1f},{p[1]:.1f}) {t:6.1f}')
print('R near 527,404'); region(it['handR'].occ, 527, 404)
print('L near 372,436'); region(it['handL'].occ, 372, 436)
