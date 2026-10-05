import sys, os, time
sys.path.insert(0, "art"); sys.path.insert(0, ".")
import QC, _qc_gown as GW
cap = {}
_g = GW.gown
def gown(*a, **k):
    p = _g(*a, **k); cap["p"] = p; return p
GW.gown = gown
t = time.time()
sc, fc = QC.figure()
print("figure %.1fs" % (time.time() - t))
for b, L, W, bd, pg in cap["p"].meta["leaves"]:
    print("base (%.0f,%.0f) L %.0f W %.1f bounds %s" % (b[0], b[1], L, W, tuple(round(v) for v in pg.bounds)))
