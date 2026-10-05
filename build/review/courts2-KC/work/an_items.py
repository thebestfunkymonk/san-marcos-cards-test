import sys, importlib.util
sys.path.insert(0,'.')
import numpy as np
from shapely.geometry import Point, LineString
spec = importlib.util.spec_from_file_location('kcmod', 'art/KC.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from deck import courtkit as K
sc = m.figure()
it = {i.name: i for i in sc.items}
print([i.name for i in sc.items])
head = it['head'].occ; beard = it['beard'].occ; mo = it['moustache'].occ
for y in range(180, 330, 6):
    ln = LineString([(250,y),(375,y)])
    def xs(g):
        x = ln.intersection(g)
        return None if x.is_empty else (round(x.bounds[0],1), round(x.bounds[2],1))
    print(y, 'head', xs(head), 'beard', xs(beard), 'hair', xs(it['hair-1'].occ))
