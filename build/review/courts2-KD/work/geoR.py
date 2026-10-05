import sys, warnings
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import importlib.util
import numpy as np
from shapely.geometry import LineString
from deck import courtkit as K
spec = importlib.util.spec_from_file_location('kdg', sys.argv[1] if len(sys.argv)>1 else 'art/KD.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
it = {i.name: i for i in sc.items}
for nm in ('sleeveR','cuffR','handR','key','handR~heel~key','handR~key'):
    g = it[nm].occ; print(nm, np.round(g.bounds,1), 'halo_zone' , None if it[nm].halo_zone is None else np.round(it[nm].halo_zone.bounds,1))
key = it['key'].occ
for y in (400,405,410,415,420,425,430,440,460,480,500,511):
    ln = LineString([(440,y),(620,y)])
    def xr(g):
        q = ln.intersection(g); return None if q.is_empty else tuple(np.round(q.bounds[::2],1))
    print(y, 'sleeve', xr(it['sleeveR'].occ), 'cuff', xr(it['cuffR'].occ), 'hand', xr(it['handR'].occ), 'key', xr(key))
sash = it['sash'].occ
for y in (470,480,490,500,505,511):
    ln = LineString([(380,y),(620,y)])
    q = ln.intersection(sash); print('sash', y, np.round(q.bounds[::2],1) if not q.is_empty else None)
fkw = dict(shaft_w=22.0, back=-1, h=38.0)
for bend in (40, 45, 50, 55, 60):
    for dist in (0.85, 0.95, 1.05):
        print(bend, dist, np.round(K.fist_wrist((546.0, 384.0), -90.0, bend=bend, dist=dist, **fkw), 1))
