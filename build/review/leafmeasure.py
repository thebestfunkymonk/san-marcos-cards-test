import sys; sys.path.insert(0,".")
import numpy as np
from shapely.geometry import LineString, Point
from deck.motifs import rice as R, forms as FM
from inkkit import geom as G
for args in [dict(x=0,y=60,heading=-14,length=170,bend=(12,-12)), dict(x=0,y=110,heading=-8,length=190,bend=(9,9)), dict(x=0,y=150,heading=0,length=150,bend=(0,0))]:
    f = R.ribbon_leaf(**args)
    mid = np.asarray(f.meta["mid"]); hw = f.meta["hw"]
    left, right, ol = FM.leaf_edges(mid, hw)
    Lm = LineString(mid); Ll = LineString(left); Lr = LineString(right)
    cv = G.Curve(mid)
    print(args["bend"], "L", round(cv.length,1))
    for t in (0.25, 0.5, 0.75):
        p = cv.at_s(t*cv.length)
        n = cv.normal_s(np.array([t*cv.length]))[0]
        tg = cv.tangent_s(t*cv.length)
        print("  t",t,"hw",round(float(hw(np.array([t*cv.length]))[0]),2),"dist L",round(Ll.distance(Point(p)),2),"dist R",round(Lr.distance(Point(p)),2), "n.t", round(float(np.dot(n,tg)),3), "|n|", round(float(np.hypot(*n)),3))
