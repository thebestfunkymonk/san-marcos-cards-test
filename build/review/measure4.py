import math
import xml.etree.ElementTree as ET
from svgelements import Path as SPath
import numpy as np
from shapely.geometry import Polygon, box, LineString
NS = "{http://www.w3.org/2000/svg}"
ROOT = "/home/luke/Projects/design/san-marcos-deck"
def geom(d, n=64):
    p = SPath(d); g = None
    for sp in p.as_subpaths():
        pts = []
        for seg in SPath(sp):
            if type(seg).__name__ == "Move": continue
            for t in np.linspace(0, 1, n, endpoint=False):
                q = seg.point(t); pts.append((q.x, q.y))
        if len(pts) < 3: continue
        pg = Polygon(pts).buffer(0)
        g = pg if g is None else g.symmetric_difference(pg)
    return g
def pip_of(stem):
    root = ET.parse(f"{ROOT}/cards/{stem}.svg").getroot()
    return [el for el in root.iter(NS+"path") if "ace-pip" in (el.get("class") or "")][0]
def width_at(g, y):
    seg = g.intersection(LineString([(0, y), (750, y)]))
    if seg.is_empty: return 0, None
    x0, _, x1, _ = seg.bounds
    return round(x1 - x0, 2), (round(x0, 2), round(x1, 2))
S = geom(pip_of("AS").get("d"))
print("AS bbox", [round(v,2) for v in S.bounds], "(brief: 340 x 374, top 140, cx 375)")
for y in (200, 262, 335, 400, 480, 481, 490, 499, 500, 505, 513):
    print("  width at y", y, width_at(S, y))
# widest y
ys = np.arange(140, 514, 0.25); ws = [width_at(S, y)[0] for y in ys]
print("  widest at y", ys[int(np.argmax(ws))], max(ws))
# lobe lower edges: lowest y where width > stem width + 40 (lobes)
lob = [y for y, w in zip(ys, ws) if w > 120]
print("  lobe lower edge y ~", lob[-1])
# cleft beside stem: find y where the region separates -> number of components along the line
def ncomp(g, y):
    seg = g.intersection(LineString([(0, y), (750, y)]))
    return len(getattr(seg, "geoms", [seg])) if not seg.is_empty else 0
split = [y for y in ys if ncomp(S, y) >= 3]
print("  3-component band (lobes + stem) y", (split[0], split[-1]) if split else None)
for stem, u in (("AH", 280*1.04), ("AC", 280), ("AD", 280)):
    g = geom(pip_of(stem).get("d"))
    b = g.bounds
    print(stem, "bbox", [round(v,2) for v in b], "w x h", round(b[2]-b[0],2), round(b[3]-b[1],2), "centre", round((b[0]+b[2])/2,2), round((b[1]+b[3])/2,2))
    if stem == "AH":
        # cleft depth: top-of-shape at x=375 minus bbox top
        seg = g.intersection(LineString([(375, 0), (375, 1050)]))
        print("   cleft depth", round(seg.bounds[1]-b[1],2), "= %.4f u" % ((seg.bounds[1]-b[1])/u), "(brief .16u)")
    if stem == "AD":
        # sagitta: distance from the chord midpoint of the upper-right side to the curve
        tip_t = (375, b[1]); tip_r = (b[2], 470)
        mid = ((tip_t[0]+tip_r[0])/2, (tip_t[1]+tip_r[1])/2)
        L = math.dist(tip_t, tip_r)
        nx, ny = (tip_r[1]-tip_t[1])/L, -(tip_r[0]-tip_t[0])/L  # normal
        # inward normal points to centre (375,470)
        if (375-mid[0])*nx + (470-mid[1])*ny < 0: nx, ny = -nx, -ny
        ray = LineString([mid, (mid[0]+nx*40, mid[1]+ny*40)])
        inter = ray.intersection(g.exterior)
        pts = [inter] if inter.geom_type == "Point" else list(getattr(inter, "geoms", []))
        dmin = min(math.dist(mid, (p.x, p.y)) for p in pts)
        print("   side length", round(L,2), "sagitta", round(dmin,2), "=", round(dmin/L*100,2), "% (brief 3 %)")
