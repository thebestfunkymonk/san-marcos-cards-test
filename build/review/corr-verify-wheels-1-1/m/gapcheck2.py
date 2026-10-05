import importlib.util, shapely
from tuck import build_tuck as NEW, _tuck_front as TF, _tuck_panels as TP, _tuck_common as K, _tuck_back as TB
spec = importlib.util.spec_from_file_location("old_bt", "../before/tuck/build_tuck.py")
OLD = importlib.util.module_from_spec(spec); spec.loader.exec_module(OLD)
p = TP.build()
for k in ("side_a", "side_b", "top", "bottom"):
    fr = p[k]; sh = fr.shape(); th = K.type_hull(fr)
    o = [x for x in OLD.foil_gaps(sh, parallel=True, type_shape=th) if "warn" not in x["rule"]]
    n = [x for x in NEW.foil_gaps(sh, parallel=True, type_shape=th) if "warn" not in x["rule"]]
    print(k, len(o), len(n), o == n)
# medallion zone geometry identical?
fa = TF.build()["foil"].shape()
TF.ROUNDEL_C = (53.0, 59.0)
fb = TF.build()["foil"].shape()
z = shapely.box(20, 150, 90, 919)
print("side zone sym diff area (y150-919):", fa.intersection(z).symmetric_difference(fb.intersection(z)).area)
z2 = shapely.box(20, 20, 750, 1050)
d = fa.symmetric_difference(fb)
print("total symdiff area", round(d.area,2), "bounds", [round(v,1) for v in d.bounds])
for g in sorted(getattr(d,'geoms',[d]), key=lambda g:-g.area)[:40]:
    b = g.bounds
    if g.area > 0.5: print('  ', round(g.area,1), [round(v,1) for v in b])
