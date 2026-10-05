import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")
from deck import build as B
from shapely.geometry import Point
mod = B.load_art(sys.argv[1])
sc = mod.figure(); sc = sc[0] if isinstance(sc, tuple) else sc
sil = sc.silhouette()
p = Point(*map(float, sys.argv[2].split(",")))
print("sil type", sil.geom_type)
polys = getattr(sil, "geoms", [sil])
for pg in polys:
    if pg.distance(p) < 20:
        print("poly area %.0f bounds %s, holes %d" % (pg.area, [round(v,1) for v in pg.bounds], len(pg.interiors)))
        for r in pg.interiors:
            from shapely.geometry import Polygon
            h = Polygon(r)
            if h.distance(p) < 20:
                print("   hole area %.1f bounds %s" % (h.area, [round(v,1) for v in h.bounds]))
for it in sc.items:
    if it.occ is not None and it.sil and it.occ.distance(p) < 8:
        print("item", it.name, "dist %.2f" % it.occ.distance(p))
