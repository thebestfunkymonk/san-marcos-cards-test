import importlib.util, sys, time
from tuck import build_tuck as NEW, _tuck_front as TF, _tuck_panels as TP
spec = importlib.util.spec_from_file_location("old_bt", "../before/tuck/build_tuck.py")
OLD = importlib.util.module_from_spec(spec); spec.loader.exec_module(OLD)
fr_new = TF.build()["foil"]
TF.ROUNDEL_C = (53.0, 59.0)
fr_old = TF.build()["foil"]
for name, fr in (("front-after", fr_new), ("front-before", fr_old)):
    sh = fr.shape()
    for lab, M in (("OLD qa", OLD), ("NEW qa", NEW)):
        g = M.foil_gaps(sh, parallel=True, type_shape=None)
        g = [x for x in g if "warn" not in x["rule"]]
        print(name, lab, len(g), g[:6])
from tuck import _tuck_common as K
print('---- with type_shape, diffs')
TF.ROUNDEL_C = (56.0, 56.0)
fr_new = TF.build()["foil"]
for name, fr in (("front-after", fr_new), ("front-before", fr_old)):
    sh = fr.shape(); th = K.type_hull(fr)
    res = {}
    for lab, M in (("OLD", OLD), ("NEW", NEW)):
        g = [x for x in M.foil_gaps(sh, parallel=True, type_shape=th) if "warn" not in x["rule"]]
        res[lab] = g
        print(name, lab, len(g), g)
