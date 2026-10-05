import sys; sys.path.insert(0,".")
import shapely, itertools
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
from inkkit import geom as G
from deck.motifs import fauna as FA, lion as L, rice as R
from collections import Counter
def crossings(f, name):
    segs = []
    for i, m in enumerate(f.marks):
        if m.kind != "stroke": continue
        for pts, cl in G.flatten(m.d, 0.1):
            if len(pts) > 1: segs.append((i, m.role, LineString(pts)))
    geoms = [s[2] for s in segs]
    tree = STRtree(geoms)
    X = []
    for ai, (i, ra, a) in enumerate(segs):
        for bi in tree.query(a):
            if bi <= ai: continue
            j, rb, b = segs[bi]
            inter = a.intersection(b)
            if inter.is_empty: continue
            for g in getattr(inter, "geoms", [inter]):
                if g.geom_type != "Point": continue
                ends = [Point(a.coords[0]), Point(a.coords[-1]), Point(b.coords[0]), Point(b.coords[-1])]
                if min(e.distance(g) for e in ends) < 1.0: continue
                X.append((ra, rb, round(g.x,1), round(g.y,1)))
    print(f"{name:26s} plain crossings {len(X):3d}", Counter((a,b) for a,b,_,_ in X).most_common(5), X[:4])
crossings(L.lion_moleca(), "lion moleca")
crossings(L.lion_andante(0,0), "lion andante")
crossings(FA.fountain_darter(60,40,100), "darter")
crossings(L.lion_mark(0,0,40), "lion mark 40")
crossings(R.rice_wreath_arc(0,0,150), "wreath arc")
crossings(R.rice_stalk(0,0), "rice stalk")
f = L.lion_andante(0,0)
segs=[]
for i, m in enumerate(f.marks):
    if m.kind != "stroke": continue
    for pts, cl in G.flatten(m.d, 0.1):
        if len(pts) > 1: segs.append((i, m.role, LineString(pts)))
for ai,(i,ra,a) in enumerate(segs):
    for bi,(j,rb,b) in enumerate(segs):
        if bi<=ai: continue
        if {ra,rb} in ({"leaf"},{"paw","ledge"},{"tail","body"}):
            inter=a.intersection(b)
            for g in getattr(inter,"geoms",[inter]):
                if g.is_empty or g.geom_type!="Point": continue
                ends=[Point(a.coords[0]),Point(a.coords[-1]),Point(b.coords[0]),Point(b.coords[-1])]
                if min(e.distance(g) for e in ends)<1.0: continue
                print(ra,rb,round(g.x,1),round(g.y,1))
