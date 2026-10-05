import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")
from deck import build as B, qa as QA
from deck.motifs import core as C
from shapely.geometry import Point
mod = B.load_art("QC")
sc, _ = mod.figure()
res = sc.compose()
p = Point(406.8, 337.3)
for i, m in enumerate(res.marks):
    if m.kind != "stroke":
        continue
    a = C.Frag([m]).shape()
    b = QA._stroke_geom(m.d, m.w, m.cap, m.join, m.miter)
    da, db = a.distance(p), b.distance(p)
    if min(da, db) < 6:
        print(i, m.role, m.w, m.cap, m.join, round(da, 2), round(db, 2), [round(v,1) for v in a.bounds], [round(v,1) for v in b.bounds])
        if abs(da-db) > 1: print("   d=", m.d[:120], "...", m.d[-200:], m.miter)
