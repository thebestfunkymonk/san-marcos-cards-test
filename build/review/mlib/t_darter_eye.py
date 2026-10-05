from rh import *
from deck.motifs import fauna as FA
from inkkit import geom as G
from shapely.geometry import Point
f = FA.fountain_darter(0, 0, 100)
x0,y0,x1,y1 = f.bbox()
solid = G.rect_d(x0-5,y0-5,x1-x0+10,y1-y0+10)
ko = C.knockout(solid, f)
g = C.region(ko)
eye = [m for m in f.marks if m.role=="eye"][0]
ex0,ey0,ex1,ey1 = G.bbox(eye.d); c = ((ex0+ex1)/2,(ey0+ey1)/2)
inside = g.intersection(Point(c).buffer(4.0))
print("jade left inside the eye disc (px^2):", inside.area, "pieces:", len(getattr(inside,'geoms',[inside])) if not inside.is_empty else 0)
print("svg path count of subpaths in ko near eye:", sum(1 for p,cl in G.flatten(ko) if Point(p[0]).distance(Point(c))<4.5))
