import os, sys
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "art"))
import importlib.util
from deck import courtkit as K
from deck import frames as F
from inkkit import geom as G
import shapely
spec = importlib.util.spec_from_file_location("jc", os.path.join(ROOT, "art/JC.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
win = K.R(F.court_clip_d("J", 511.0))
WA = 430811 / 2
# per item visible fill area by layer (approx: item fill minus occluders in front)
acc = shapely.Polygon()
rows = []
for it in reversed(sc.items):
    for lay in ("jade", "red", "gold"):
        fs = [G.to_shape(mk.d, tol=0.1) for mk in it.frag.marks if mk.kind == "fill" and mk.layer == lay and mk.d]
        if fs:
            u = shapely.union_all(fs).intersection(win).difference(acc)
            rows.append((it.name, lay, u.area))
    if it.occ is not None:
        acc = acc.union(it.occ)
tot = {}
for n, l, a in rows:
    tot[l] = tot.get(l, 0) + a
for n, l, a in sorted(rows, key=lambda r: (r[1], -r[2])):
    if a > 50: print(f"{l:5s} {n:12s} {a:8.0f}  {100*a/WA:5.2f}%")
print({k: round(100 * v / WA, 2) for k, v in tot.items()})
