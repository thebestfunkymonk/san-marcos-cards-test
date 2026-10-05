import sys
root = sys.argv[1]; sys.path.insert(0, root)
import numpy as np, shapely
from shapely.geometry import box
from deck.motifs import core as C
from tuck import _tuck_front as TF
wheel = TF.roundels().shape().intersection(box(0, 0, 200, 200))
print("TF ROUNDEL_C", TF.ROUNDEL_C, "wheel bounds", [round(v, 2) for v in wheel.bounds])
for name, f in (("rules", TF.frame_rules()), ("ladders", TF.side_ladders()), ("bands", TF.top_band())):
    for m in f.marks:
        s = C.Frag([m]).shape()
        for g in getattr(s, "geoms", [s]):
            if g.intersects(box(0, 0, 200, 200)) and g.distance(wheel) < 40:
                print(f"  {name:7s} w={m.w} d_wheel={g.distance(wheel):.2f} bounds=({g.bounds[0]:.2f},{g.bounds[1]:.2f},{g.bounds[2]:.2f},{g.bounds[3]:.2f})")
