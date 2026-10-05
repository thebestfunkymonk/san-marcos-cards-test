"""which marks are near a point: python work/ac-followup/who.py 'KW' x,y [x,y ...]"""
import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, "work/ac-followup")
import numpy as np, shapely
import reed_w as RW
from art import _aces_common as A
from inkkit import geom as G
kw = eval(sys.argv[1])
r = kw.pop("r", 190.0)
f = A.behind(RW.wreath(375.0, A.CY, r, **kw), "C")
for xy in sys.argv[2:]:
    x, y = map(float, xy.split(","))
    P = shapely.Point(x, y)
    print(f"-- {x},{y}")
    for i, m in enumerate(f.marks):
        for pts, cl in G.flatten(m.d, 0.05):
            if len(pts) < 2: continue
            ln = shapely.LinearRing(pts) if cl and len(pts) > 2 else shapely.LineString(pts)
            d = ln.distance(P) - (m.w / 2 if m.kind == "stroke" else 0)
            if d < 4.0:
                print(f"  mark{i} {m.role:10s} {m.kind} d={d:.2f} n={len(pts)} start={np.round(pts[0],1)} end={np.round(pts[-1],1)}")
