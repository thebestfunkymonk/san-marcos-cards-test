"""geo.py [module] — geometric facts of the QD scene."""
import sys, os, importlib.util, warnings
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
warnings.simplefilter("ignore")
import numpy as np, shapely
from shapely.geometry import LineString, Point, box
from deck import courtkit as K
path = sys.argv[1] if len(sys.argv) > 1 else ROOT + "/art/QD.py"
spec = importlib.util.spec_from_file_location("qdmod", path); m = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.dirname(os.path.abspath(path))); spec.loader.exec_module(m)
sc = m.figure()
it = {i.name: i for i in sc.items}
for n in it:
    o = it[n].occ
    if o is not None and not o.is_empty:
        print(f"{n:28s} bbox {tuple(round(v,1) for v in o.bounds)} halo {it[n].halo}")
sil = sc.silhouette()
def xs_at(g, y):
    ln = LineString([(0, y), (800, y)]).intersection(g)
    return [tuple(round(v, 1) for v in (s.bounds[0], s.bounds[2])) for s in K._lines_of(ln)]
print("\n y  | silhouette | sleeveR | staff | handR | sleeveL | handL | paintbrush")
for y in range(380, 512, 10):
    print(y, xs_at(sil, y), xs_at(it['sleeveR'].occ, y), xs_at(it['staff'].occ, y), xs_at(it['handR'].occ, y),
          xs_at(it['sleeveL'].occ, y), xs_at(it['handL'].occ, y), xs_at(it['paintbrush'].occ, y))
# chain stones near the left hand
cape = it['cape']
