"""probe.py [module] — QD hand/chain/sleeve geometry facts."""
import sys, os, importlib.util, warnings, math
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
warnings.simplefilter("ignore")
import numpy as np, shapely
from shapely.geometry import LineString, Point, box
from deck import courtkit as K
path = sys.argv[1] if len(sys.argv) > 1 else ROOT + "/art/QD.py"
spec = importlib.util.spec_from_file_location("qdmod", path); m = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.dirname(os.path.abspath(path))); spec.loader.exec_module(m)
K.HAND_LOG.clear()
sc = m.figure()
it = {i.name: i for i in sc.items}
print("items:", [i.name for i in sc.items])
print("HAND_LOG", K.HAND_LOG)
cp = it['cape']
def xs(g, y):
    ln = LineString([(0, y), (800, y)]).intersection(g)
    return [tuple(round(v, 1) for v in (s.bounds[0], s.bounds[2])) for s in K._lines_of(ln)]
for n in ('handL', 'handR', 'cuffL', 'cuffR', 'sleeveL', 'sleeveR'):
    print(n, tuple(round(v, 1) for v in it[n].occ.bounds), 'area', round(it[n].occ.area))
# left: chain rail (paper strokes) of the cape near the stem
Lcape = it['cape']
print("\n y | stem | handL | cape(red) | sleeveL")
for y in range(390, 511, 8):
    print(y, xs(it['paintbrush'].occ, y), xs(it['handL'].occ, y), xs(Lcape.occ, y)[:2], xs(it['sleeveL'].occ, y))
print("\n y | staff | handR | cuffR | sleeveR | cape")
for y in range(380, 511, 8):
    print(y, xs(it['staff'].occ, y), xs(it['handR'].occ, y), xs(it['cuffR'].occ, y), xs(it['sleeveR'].occ, y), xs(Lcape.occ, y)[-1:])
