import sys, re
sys.path.insert(0, 'build/review/corr-verify-JOKER_BLACK-2-1'); sys.path.insert(0, '.')
import shapely
from shapes import load, shape_of
fn = sys.argv[1] if len(sys.argv) > 1 else 'cards/JOKER-BLACK.svg'
L = load(fn)
for lid, items in L.items():
    for i, it in enumerate(items):
        s = shape_of(it)
        print(lid, i, it['cls'], it['fill'], it['sw'], it['cap'], round(s.area,1), [round(v,1) for v in s.bounds], len(getattr(s,'geoms',[s])))
