"""Visible area of each scene item (top half, clipped to the court clip), in % of the QA window (both halves)."""
import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import shapely
from shapely.geometry import Polygon
from deck import courtkit as K, frames as F
import importlib.util
spec = importlib.util.spec_from_file_location("qh", sys.argv[1] if len(sys.argv) > 1 else "art/QH.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
clip = K.R(F.court_clip_d("Q", 511.0))
W = 430811.0
acc = Polygon()
rows = []
for it in reversed(sc.items):
    if it.occ is None or it.occ.is_empty:
        continue
    vis = it.occ.intersection(clip).difference(acc)
    acc = acc.union(it.occ)
    rows.append((it.name, 2 * vis.area / W * 100))
tot = {}
for n, a in rows:
    key = n.split("_")[0].rstrip("0123456789-")
    tot[key] = tot.get(key, 0) + a
for k, v in sorted(tot.items(), key=lambda q: -q[1]):
    print(f"{k:14s} {v:5.2f}")
print("covered", 2 * acc.intersection(clip).area / W * 100)
