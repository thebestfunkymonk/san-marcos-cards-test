import sys, warnings
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np
from art import KD
from deck import courtkit as K
from shapely.geometry import LineString
sc = KD.figure()
it = {i.name: i for i in sc.items}
op = K.R(K.Path((347.0, 292.0)).sag((KD.OPEN_TR, 292.0), -10.0).sag((493.0, 545.0), KD.OPEN_SAG).line((259.0, 545.0)).sag((347.0, 292.0), KD.OPEN_SAG_L).close().d)
for y in range(420, 512, 6):
    ln = LineString([(420, y), (560, y)])
    q = ln.intersection(op.exterior); xo = [round(p.x,1) for p in getattr(q,'geoms',[q])] if not q.is_empty else None
    s = ln.intersection(it['sleeveR'].occ); c = ln.intersection(it['cuffR'].occ)
    print(y, 'open edge', xo, 'sleeve', None if s.is_empty else round(s.bounds[0],1), 'cuff', None if c.is_empty else round(c.bounds[0],1))
