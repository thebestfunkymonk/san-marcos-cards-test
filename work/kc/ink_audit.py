import sys, collections
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import numpy as np
from deck import courtkit as K
from deck.motifs import core as C
import importlib.util
spec = importlib.util.spec_from_file_location("kc", "/home/luke/Projects/design/san-marcos-deck/art/KC.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
f = sc.compose()
win = 430811.0 / 2  # one half
acc = collections.defaultdict(float)
for mk in f.marks:
    try:
        g = K.R(K.G.from_skia(mk.skia()))
        a = g.area
    except Exception as e:
        continue
    acc[(mk.layer if hasattr(mk,'layer') else '?', mk.role)] += a
tot = collections.defaultdict(float)
for (L, r), a in sorted(acc.items(), key=lambda kv: -kv[1]):
    tot[L] += a
    if a / win * 100 > 0.15:
        print(f"{L:5s} {r:12s} {a/win*100:5.2f}%")
print({L: round(a / win * 100, 2) for L, a in tot.items()})
