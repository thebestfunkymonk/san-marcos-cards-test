import sys
root = sys.argv[1]; sys.path.insert(0, root)
import numpy as np, shapely
from shapely.geometry import box, LineString
from art import _back_frame as BF
from deck.motifs import core as C
from inkkit import geom as G
fr = BF.frame()
wheel = BF.roundels().shape().intersection(box(0, 0, 200, 200))
print("corner ripple pieces in TL quadrant (centreline length, ends):")
for m in fr["corner"].marks:
    for P, cl in G.flatten(m.d, 0.05):
        P = np.asarray(P)
        if P[:, 0].max() < 375 and P[:, 1].max() < 525:
            L = LineString(P)
            r = np.hypot(P[:, 0] - BF.ROUNDEL_C[0], P[:, 1] - BF.ROUNDEL_C[1]).mean()
            print(f"   r={r:6.1f} len={L.length:6.1f} ends=({P[0,0]:.1f},{P[0,1]:.1f})-({P[-1,0]:.1f},{P[-1,1]:.1f})")
# nearest band (wave) element to the wheel
bs = fr["bands"].shape()
gs = [g for g in getattr(bs, "geoms", [bs]) if g.bounds[0] < 375 and g.bounds[1] < 200]
gs.sort(key=lambda g: g.distance(wheel))
for g in gs[:2]:
    print("wave piece d_wheel=%.2f bounds=%s" % (g.distance(wheel), [round(v, 2) for v in g.bounds]))
# field (lens offset contours) near corner
fs = fr["field"].shape()
gs = [g for g in getattr(fs, "geoms", [fs]) if g.bounds[0] < 200 and g.bounds[1] < 200]
gs.sort(key=lambda g: g.distance(wheel))
print("field nearest d_wheel=%.2f" % gs[0].distance(wheel) if gs else "no field")
# ripple vs field min distance
rs = fr["corner"].shape().intersection(box(0, 0, 375, 525))
print("ripple-field min dist %.2f" % rs.distance(fs.intersection(box(0, 0, 375, 525))))
# ripple vs rules / bands / sides distances
for k in ("rules", "bands", "sides", "lens"):
    print("ripple-%s min dist %.2f" % (k, rs.distance(fr[k].shape().intersection(box(0, 0, 375, 525)))))
