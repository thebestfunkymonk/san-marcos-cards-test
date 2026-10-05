import sys, collections
sys.path.insert(0, "art")
import numpy as np, shapely
import QC
from inkkit import geom as G
from deck import courtkit as K
sc, fc = QC.figure()
fr = QC.compose_scene(sc)
win = shapely.box(139, 55, 611, 511)
acc = collections.defaultdict(list)
for m in fr.marks:
    if m.layer != "ink" or not m.d: continue
    g = K.R(G.from_skia(m.skia()))
    acc[m.role].append(g.intersection(win))
tot = shapely.union_all([shapely.union_all(v) for v in acc.values()]).area
print("ink half area", round(tot), "pct of window", round(100 * tot / win.area, 2))
rows = sorted(((shapely.union_all(v).area, r) for r, v in acc.items()), reverse=True)
for a, r in rows[:30]:
    print(f"{r:18s} {a:8.0f} {100*a/win.area:5.2f}%")
