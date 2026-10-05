"""Visible area of each Scene item (top half, clipped to the court clip), in % of the half window."""
import sys, importlib.util
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import courtkit as K, frames as F
from shapely.geometry import Polygon
path = sys.argv[1] if len(sys.argv) > 1 else "/home/luke/Projects/design/san-marcos-deck/art/KH.py"
spec = importlib.util.spec_from_file_location("m", path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
clip = K.R(F.court_clip_d("K", 511.0))
win = K.R(F.art_window_d()).intersection(K.box(0, 0, 750, 511)).area
acc = Polygon()
rows = []
for it in reversed(sc.items):
    if it.occ is None or it.occ.is_empty:
        continue
    vis = it.occ.intersection(clip).difference(acc)
    rows.append((it.name, vis.area / win * 100))
    acc = acc.union(it.occ)
for n, a in reversed(rows):
    print(f"{n:14s} {a:5.1f}")
print(f"{'FIGURE':14s} {acc.intersection(clip).area / win * 100:5.1f}   (window half {win:.0f} px2)")
