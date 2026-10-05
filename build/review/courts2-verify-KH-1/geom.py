import sys
sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import Point
from art import KH, _kh_parts as KP
from deck import courtkit as K
robe_m, rip, robe_inner = KP.robe(KH.ROBE, border=30.0, pitch=(96.0, 36.0), origin=(K.AX, 312.0))
robe = robe_m.shape
WL, WR = KH.WRISTS
slL, cfL = K.sleeve(K.SleeveSpec(wrist=WL, color=K.JADE, cuff_color=K.JADE, **KH.SLEEVE_L))
slR, cfR = K.sleeve(K.SleeveSpec(wrist=WR, color=K.JADE, cuff_color=K.JADE, **KH.SLEEVE_R))
print("WL", WL, "WR", WR, "ARM_L_BASE", KH.ARM_L_BASE, "ARM_R_BASE", KH.ARM_R_BASE)
for name, cf, sl in (("L", cfL, slL), ("R", cfR, slR)):
    poly = cf.shape
    coords = np.asarray(poly.exterior.coords)
    # simplify to corners
    s = poly.simplify(1.0)
    cs = np.asarray(s.exterior.coords)[:-1]
    print(name, "cuff corners (simplified):")
    rb = robe.exterior
    for c in cs:
        print("   ", np.round(c, 1), "dist to robe outline %.1f" % rb.distance(Point(c)))
    # where robe outline crosses sleeve top edge
    inter = rb.intersection(sl.shape.union(cf.shape).exterior)
    print("  robe outline x sleeve/cuff boundary:", inter.wkt[:300])
