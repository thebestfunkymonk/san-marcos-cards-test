# marks_at.py x0 y0 x1 y1 : list final marks (after compose) intersecting the box
import sys; sys.path.insert(0,'.')
from art import JH as m
from deck import courtkit as K
from inkkit import geom as G
import shapely
x0,y0,x1,y1 = map(float, sys.argv[1:5])
sc = m.figure(); res = m.compose(sc)
b = shapely.box(x0,y0,x1,y1)
for i,mk in enumerate(res.marks):
    if not mk.d: continue
    try: g = K.R(G.from_skia(mk.skia()))
    except Exception as e: continue
    if g.intersects(b):
        print(i, mk.kind, mk.role, mk.layer, mk.w, mk.cap if hasattr(mk,'cap') else '', tuple(round(v,1) for v in g.intersection(b).bounds))
