import warnings, sys, numpy as np, shapely
sys.path.insert(0, '.')
from deck import courtkit as K
import art.KH as KH
warnings.simplefilter("always")
with warnings.catch_warnings(record=True) as wl:
    sc = KH.figure()
    for w in wl: print("WARN", w.message)
print("HAND_LOG", getattr(K, "HAND_LOG", None))
items = {it.name: it for it in sc.items}
print([n for n in items])
for n in ("handL", "handR"):
    it = items[n]
    g = it.occ
    print(n, "bounds", [round(v,1) for v in g.bounds], "area", round(g.area,1))
# face egg
fc = K.face(KH.HEAD, "frontal", **KH.FACE_KW)
print("face head bounds", [round(v,1) for v in fc.head.bounds] if hasattr(fc.head,'bounds') else None)
hd = K.R(fc.head) if not hasattr(fc.head, 'bounds') else fc.head
print("face egg bounds", [round(v,1) for v in hd.bounds])
for n in ("head","hair-1","beard","crown"):
    print(n, [round(v,1) for v in items[n].occ.bounds])
# other kings' hands for size comparison
import importlib
for cid in ("KS","KC","KD"):
    m = importlib.import_module(f"art.{cid}")
    s2 = m.figure()
    for it in s2.items:
        if it.name.startswith("hand") or it.name.startswith("fist"):
            if it.occ is not None and not it.occ.is_empty:
                print(cid, it.name, [round(v,1) for v in it.occ.bounds], round(it.occ.area,1))
