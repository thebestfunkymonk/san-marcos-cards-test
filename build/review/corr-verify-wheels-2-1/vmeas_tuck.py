import sys
root = sys.argv[1]; sys.path.insert(0, root)
import numpy as np, shapely
from shapely.geometry import box
from deck.motifs import core as C
from tuck import _tuck_front as TF, _tuck_back as TB, _tuck_common as K
from tuck import build_tuck as BT
b = BT.build_all()
def report(label, foil, wheel_c):
    s = foil.shape()
    geoms = [g for g in getattr(s, "geoms", [s])]
    q = box(0, 0, 250, 350)
    # the wheel = the piece containing a point on its outer ring
    cx, cy = wheel_c
    wheel = [g for g in geoms if g.distance(shapely.Point(cx - 26, cy)) < 0.5][0]
    print(label, "wheel bounds", [round(v, 2) for v in wheel.bounds])
    for g in geoms:
        if g is wheel or not g.intersects(q): continue
        d = g.distance(wheel)
        if d < 16:
            print("   d_wheel=%6.2f bounds=(%.2f,%.2f,%.2f,%.2f)" % ((d,) + g.bounds))
report("FRONT", b["front"]["foil"], TF.ROUNDEL_C)
bc = (TF._BF.ROUNDEL_C[0] + TB.DX, TF._BF.ROUNDEL_C[1] + TB.DY)
report("BACK", b["back"]["foil"], bc)
# tuck back side ladders: top rung y and distance to wheel
lad = TB.side_ladders(None) if TB.side_ladders.__code__.co_argcount else TB.side_ladders()
ls = lad.shape()
wheel = b["back"]["foil"].shape()
lg = [g for g in getattr(ls, "geoms", [ls]) if g.bounds[0] < 100 and g.bounds[1] < 534]
lg.sort(key=lambda g: g.bounds[1])
print("tuck back side ladder topmost pieces:", [[round(v, 2) for v in g.bounds] for g in lg[:3]])
