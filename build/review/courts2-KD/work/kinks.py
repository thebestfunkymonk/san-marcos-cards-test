import sys, warnings
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import importlib.util, numpy as np
from deck import courtkit as K
spec = importlib.util.spec_from_file_location('kdk', sys.argv[1] if len(sys.argv)>1 else 'art/KD.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
it = {i.name: i for i in sc.items}
for nm in ('handL', 'handR'):
    g = it[nm].occ
    xy = np.array(g.exterior.coords)[:-1]
    n = len(xy)
    print(nm, 'npts', n)
    for i in range(n):
        a, b, c = xy[i-1], xy[i], xy[(i+1) % n]
        v1, v2 = b - a, c - b
        l1, l2 = np.hypot(*v1), np.hypot(*v2)
        if l1 < 1e-6 or l2 < 1e-6: continue
        t = np.degrees(np.arctan2(v1[0]*v2[1]-v1[1]*v2[0], v1@v2))
        if abs(t) > 12:
            print(f'  turn {t:6.1f} at ({b[0]:.1f},{b[1]:.1f}) seg {l1:.2f}/{l2:.2f}')
