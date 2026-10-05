"""probe.py x y r : strokes/fills of the composed KH near (x, y) and the heal log entries there."""
import sys, pickle, os
import numpy as np
from shapely.geometry import Point, LineString
sys.path.insert(0, '.')
from art import KH
from deck import courtkit as K
from inkkit import geom as G
x, y, r = map(float, sys.argv[1:4])
cache = 'build/review/courts3-KH/work/_composed.pkl'
sc = KH.figure()
res = sc.compose()
q = Point(x, y).buffer(r)
for m in res.marks:
    if not m.d: continue
    try:
        g = K.R(G.from_skia(m.skia()))
    except Exception as e:
        continue
    if g.intersects(q):
        info = f"{m.kind:6s} layer={getattr(m,'layer',None)} role={m.role} w={m.w} cap={m.cap}"
        if m.kind == 'stroke':
            for p, closed in G.flatten(m.d, 0.05):
                ln = LineString(p) if len(p) > 1 else None
                if ln is not None and ln.distance(Point(x, y)) < r + 4:
                    e0, e1 = p[0], p[-1]
                    info2 = f" sub closed={closed} n={len(p)} start=({e0[0]:.2f},{e0[1]:.2f}) end=({e1[0]:.2f},{e1[1]:.2f}) dist={ln.distance(Point(x,y)):.2f}"
                    print(info + info2)
        else:
            print(info)
for e in sc.heal_log:
    s = str(e)
    import re
    nums = [float(v) for v in re.findall(r'-?\d+\.\d+', s)]
    pts = list(zip(nums[::2], nums[1::2]))
    if any(abs(a - x) < r + 8 and abs(b - y) < r + 8 for a, b in pts):
        print('HEAL', s[:300])
