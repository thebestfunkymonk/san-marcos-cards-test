"""pockets.py [x y r]: non-ink pockets inside the composed ink (holes < 6 px² and closing(1.0) fills) near points."""
import sys
sys.path.insert(0, '.')
import shapely
from shapely.geometry import Point, box
from art import KH
from deck import courtkit as K
from inkkit import geom as G
res = KH.figure().compose()
a = sys.argv[1:]
zone = Point(float(a[0]), float(a[1])).buffer(float(a[2])) if a else box(100, 40, 650, 511)
ink = []
for m in res.marks:
    if m.d and m.layer == 'ink':
        g = K.R(G.from_skia(m.skia()))
        if g.intersects(zone):
            ink.append(g)
ink = shapely.union_all(ink).buffer(0)
holes = []
for pg in K._polys_of(ink):
    for r_ in pg.interiors:
        h = shapely.Polygon(r_)
        if h.area < 6.0 and h.intersects(zone):
            holes.append(h)
for h in sorted(holes, key=lambda h: h.area):
    c = h.centroid
    print(f"hole area={h.area:.3f} at ({c.x:.2f},{c.y:.2f}) bounds={tuple(round(v,2) for v in h.bounds)}")
cl = ink.buffer(1.0, quad_segs=12).buffer(-1.0, quad_segs=12).difference(ink).intersection(zone)
for g in sorted(K._polys_of(cl), key=lambda g: -g.area)[:40]:
    if g.area > 0.15:
        c = g.centroid
        print(f"close1 area={g.area:.3f} at ({c.x:.2f},{c.y:.2f})")
