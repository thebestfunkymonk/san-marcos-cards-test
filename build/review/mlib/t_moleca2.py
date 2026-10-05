from rh import *
from deck.motifs import lion as LI
from deck.motifs.sheet_figurative import spade_live
from inkkit import geom as G
f = LI.lion_moleca(375, 262, silhouette=spade_live())
rows = []
for m in f.marks:
    if m.kind != "stroke": continue
    for p, cl in G.flatten(m.d, 0.05):
        if cl: continue
        L = G.Curve(p).length
        if L < 10 and m.role not in ("hatch", "toe"):
            rows.append((m.role, round(L, 2), tuple(p.mean(axis=0).round(1))))
for r in sorted(rows, key=lambda r: r[1]): print(r)
