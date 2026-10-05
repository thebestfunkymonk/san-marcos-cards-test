"""Visible area of each Scene item (top half, art window, above the band), % of the half window."""
import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")
import shapely
from deck import courtkit as K, frames as F
import QC
sc, fc = QC.figure()
win = K.R(F.court_clip_d("Q", 511.0))
tot = win.area
acc = shapely.Polygon()
rows = []
for it in reversed(sc.items):
    if it.occ is None or it.occ.is_empty:
        continue
    vis = it.occ.intersection(win).difference(acc)
    rows.append((it.name, vis.area / tot * 100))
    acc = acc.union(it.occ)
for n, a in reversed(rows):
    print(f"{n:16s} {a:5.1f}")
print("figure total", round(acc.intersection(win).area / tot * 100, 1), " background paper", round(100 - acc.intersection(win).area / tot * 100, 1))
