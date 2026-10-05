"""Vector measurements of the TL corner of the card back frame: every frame piece near the wheel."""
import sys, json
root = sys.argv[1]
sys.path.insert(0, root)
import numpy as np, shapely
from shapely.geometry import box, Point
from art import _back_frame as BF
from inkkit import geom as G
fr = BF.frame()
wheel = BF.roundels().shape()
tl = box(0, 0, 200, 200)
wtl = wheel.intersection(tl)
print("ROUNDEL_C", BF.ROUNDEL_C, "wheel TL bounds", [round(v, 2) for v in wtl.bounds])
x0, y0, x1, y1 = wtl.bounds
print("  jade gap side %.2f top %.2f" % (x0 - 37.5, y0 - 37.5))
for name, f in fr.items():
    if name == "roundels":
        continue
    for m in f.marks:
        sh = m.shape() if hasattr(m, "shape") else None
        # per mark: split into polygons
        from deck.motifs import core as C
        s = C.Frag([m]).shape()
        for g in getattr(s, "geoms", [s]):
            if g.is_empty: continue
            if g.distance(wtl) < 14 and g.intersects(box(0, 0, 200, 200)):
                gb = g.bounds
                print(f"  {name:8s} w={getattr(m,'w',None)} role={getattr(m,'role',None)} d_wheel={g.distance(wtl):.2f} bounds=({gb[0]:.2f},{gb[1]:.2f},{gb[2]:.2f},{gb[3]:.2f}) area={g.area:.1f}")
print("n_waves", fr["bands"].meta.get("n_waves") if hasattr(fr["bands"], "meta") else None)
