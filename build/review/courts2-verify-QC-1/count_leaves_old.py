import sys, os
root = "/home/luke/Projects/design/san-marcos-deck/build/review/courts2-verify-QC-1/oldroot"
os.chdir(root); sys.path.insert(0, root); sys.path.insert(0, root + "/art"); sys.path.append("/home/luke/Projects/design/san-marcos-deck")
import _qc_gown as GW
orig = GW.gown
res = {}
def wrap(*a, **k):
    p = orig(*a, **k)
    res["placed"] = p.meta["leaves"]
    return p
GW.gown = wrap
import QC
sc, _ = QC.figure()
for b, L, W, bd, pg in res["placed"]:
    print("leaf base=(%.0f,%.0f) L=%.0f bounds=%s" % (b[0], b[1], L, tuple(round(v) for v in pg.bounds)))
print("n =", len(res["placed"]))
