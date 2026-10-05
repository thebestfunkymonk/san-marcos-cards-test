from rh import *
import traceback
from deck.motifs import geometric as M
from deck.motifs import rice as RI
from inkkit import geom as G
# 1. warnings lost on composition
a = M.ripple_rings(0, 0, 60, 8, ratio=1, ry_ratio=8/60, mode="similar")     # warns
b = M.fault_step(0, 100, 50, double=6)                                        # warns
print("a warns:", a.meta.get("warnings")); print("b warns:", b.meta.get("warnings"))
print("a + b warns:", (a + b).meta.get("warnings"))
c = C.frag(a, b); print("frag(a, b) warns:", c.meta.get("warnings"))
print("a still:", a.meta.get("warnings"))
# 2. shear accepted as 'rigid'
f = C.stroke("M0 0L10 0")
try:
    s = f.transformed((1, 0, 0.7, 1, 0, 0)); print("shear ACCEPTED:", s.marks[0].d)
except ValueError as e: print("shear rejected", e)
try:
    s = f.transformed((0.6, 0.8, 0, 1.0/0.6, 0, 0)); print("non-orthogonal det=1 ACCEPTED:", s.marks[0].d)
except ValueError as e: print("rejected", e)
# 3. rice_wreath with a d-string path (README: 'd-string or points')
for p in ("M375 700 A 175 175 0 0 0 526.6 557.5", "M375 700 L 520 560"):
    try:
        w = RI.rice_wreath(p, axis=375); print("rice_wreath(d) ok, pairs", w.meta["n_pairs"])
    except Exception as e:
        print("rice_wreath(d-string) FAILED:", type(e).__name__, e)
# 4. comb_spray with d-string & points both fine?
try:
    M.comb_spray("M0 0 A 60 60 0 0 1 80 -40", cone=8); print("comb_spray arc ok")
except Exception as e: print("comb_spray fail", e)
