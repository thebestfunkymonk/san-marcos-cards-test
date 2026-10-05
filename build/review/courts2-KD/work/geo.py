import sys, warnings
sys.path.insert(0, '.')
warnings.simplefilter('ignore')
import importlib.util
import numpy as np
from deck import courtkit as K
spec = importlib.util.spec_from_file_location('kdg', sys.argv[1] if len(sys.argv)>1 else 'art/KD.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
it = {i.name: i for i in sc.items}
print([i.name for i in sc.items])
cl = it['cuffL'].occ
print('cuffL', [tuple(round(v,1) for v in c) for c in list(cl.exterior.coords)[::max(1,len(cl.exterior.coords)//12)]])
xs = np.array(cl.exterior.coords)
print('cuffL lowest pts', sorted([tuple(np.round(p,1)) for p in xs], key=lambda p:-p[1])[:3])
sl = it['sleeveL'].occ
for y in (478,482,485,490,495,500,505,511):
    from shapely.geometry import LineString
    ln = LineString([(200,y),(450,y)]).intersection(sl.union(cl))
    print(y, ln.bounds)
