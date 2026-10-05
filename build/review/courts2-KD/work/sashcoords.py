import sys, warnings; sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import importlib.util, numpy as np, shapely
from deck import courtkit as K
spec = importlib.util.spec_from_file_location('kdc', sys.argv[1] if len(sys.argv)>1 else 'art/KD.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
p0, p1 = np.array(m.SASH[0]), np.array(m.SASH[1]); u = (p1-p0)/np.linalg.norm(p1-p0); n = np.array([u[1], -u[0]])
def to_sn(xy): d = xy - p0; return np.column_stack([d@u - m.GRIP_T, d@n])
it = {i.name: i for i in sc.items}
for name in ('handL','clasp','sash','cuffL'):
    g = it[name].occ
    loc = shapely.transform(g, to_sn)
    print(name, 'bounds (ds,n):', [round(v,1) for v in loc.bounds])
h = shapely.transform(it['handL'].occ, to_sn)
# n-extent of the hand per ds
for ds in range(-30, 36, 3):
    ln = shapely.box(ds-0.01, -200, ds+0.01, 200).intersection(h)
    if not ln.is_empty: print(ds, [round(v,1) for v in (ln.bounds[1], ln.bounds[3])])
sash = shapely.transform(it['sash'].occ, to_sn)
for ds in (-40,-30,-20,-10,0,10,20,30,40):
    ln = shapely.box(ds-0.01, -200, ds+0.01, 200).intersection(sash)
    print('sash', ds, [round(v,1) for v in (ln.bounds[1], ln.bounds[3])] if not ln.is_empty else None)
cl = shapely.transform(it['clasp'].occ, to_sn); print('clasp', [round(v,1) for v in cl.bounds])
