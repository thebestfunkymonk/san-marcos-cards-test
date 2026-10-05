import sys, numpy as np
sys.path.insert(0,'.')
from deck import courtkit as K
from art import KC
from shapely.geometry import LineString, Point
import shapely
fc = K.face(KC.HEAD, "frontal", age="elder", **KC.FACE)
hs = K.HairSpec(top=(-52.0, -30.0), bulge=(-64.0, 40.0), bottom=(-53.0, 110.0), ribbons=4)
hp = K.hair_fall(fc, -1, hs)
head = fc.head if not isinstance(fc.head,str) else K.R(fc.head)
head = K.R(fc.head)
hb = head.boundary
for m in hp.lines.marks:
    if m.role in ('current',):
        ls = K._stroke_lines(m.d)
        for l in ls:
            c = np.asarray(l.coords)
            outside = [ (x,y, hb.distance(Point(x,y)) * (1 if not head.contains(Point(x,y)) else -1)) for x,y in c[::max(1,len(c)//40)]]
            print(m.role, m.width if hasattr(m,'width') else '', len(c))
            for x,y,d in outside:
                if y<260: print(f'   ({x:.1f},{y:.1f}) d={d:.1f}')
