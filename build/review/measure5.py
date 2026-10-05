import importlib, math
from shapely.geometry import LineString
from inkkit import geom as G
import deck.pips as P
def comps(g, y):
    s = g.intersection(LineString([(0, y), (2000, y)]))
    parts = list(getattr(s, "geoms", [s])) if not s.is_empty else []
    return [(round(p.bounds[0],2), round(p.bounds[2],2)) for p in parts]
for fil in (0.035, 0.0):
    P.CROTCH_FILLET = fil
    P.unit_d.cache_clear(); P._unit_bbox.cache_clear()
    g = G.to_shape(P.pip_top_d("S", 340, 375, 140), tol=0.05)
    band = [y/4 for y in range(1500, 1700) if len(comps(g, y/4)) >= 3]
    print(f"fillet {fil}: lobe/stem split y {band[0] if band else None}..{band[-1] if band else None}")
    for y in (392, 395, 400, 405, 410):
        c = comps(g, y); mid = [p for p in c if p[0] < 375 < p[1]]
        print("   y", y, "components", c, "stem w", round(mid[0][1]-mid[0][0],2) if len(c)>=3 else "(merged)")
    # club, index size: pinhole check / crotch
    gc = G.to_shape(P.pip_top_d("C", 62, 84, 164), tol=0.01)
    print("   club@62 interiors (holes):", len(getattr(gc, "interiors", [])) if gc.geom_type=="Polygon" else gc.geom_type)
