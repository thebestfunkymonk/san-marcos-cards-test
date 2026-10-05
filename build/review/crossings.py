import sys; sys.path.insert(0,".")
import shapely, itertools
from shapely.geometry import LineString, Point
from inkkit import geom as G
from deck.motifs import fauna as FA
f = FA.blind_salamander(165,165)
from collections import Counter
print(Counter(m.role for m in f.marks))
segs = []
for i, m in enumerate(f.marks):
    if m.kind != "stroke": continue
    for pts, cl in G.flatten(m.d, 0.1):
        if len(pts) > 1: segs.append((i, m.role, LineString(pts)))
X = []
for (i, ra, a), (j, rb, b) in itertools.combinations(segs, 2):
    if a is b: continue
    inter = a.intersection(b)
    if inter.is_empty: continue
    for g in getattr(inter, "geoms", [inter]):
        if g.geom_type != "Point": continue
        # ignore touching at endpoints
        ends = [Point(a.coords[0]), Point(a.coords[-1]), Point(b.coords[0]), Point(b.coords[-1])]
        if min(e.distance(g) for e in ends) < 1.0: continue
        X.append((ra, rb, round(g.x,1), round(g.y,1)))
print(len(X))
print(Counter((a,b) for a,b,_,_ in X))
print(X[:12])
