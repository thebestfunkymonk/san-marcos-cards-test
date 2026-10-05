import sys, collections
sys.path.insert(0, "art"); sys.path.insert(0, ".")
import QC
from deck import courtkit as K
from inkkit import geom as G
import shapely
sc, fc = QC.figure()
win = shapely.box(139, 55, 611, 505)
rows = []
for it in sc.items:
    gs = collections.defaultdict(list)
    for m in it.frag.marks:
        if m.layer != "ink" or not m.d: continue
        for pts, closed in G.as_polys(m.d, 0.3):
            if len(pts) < 2: continue
            if m.kind == "stroke":
                g = (shapely.LinearRing(pts) if closed and len(pts) > 2 else shapely.LineString(pts)).buffer(m.w / 2, quad_segs=4)
            else:
                if len(pts) < 3: continue
                g = shapely.Polygon(pts).buffer(0)
            gs[m.role].append(g)
    if gs:
        tot = shapely.union_all([g for v in gs.values() for g in v]).intersection(win).area
        top = sorted(((shapely.union_all(v).intersection(win).area, r) for r, v in gs.items()), reverse=True)[:4]
        rows.append((tot, it.name, [(round(a), r) for a, r in top]))
for tot, nm, top in sorted(rows, key=lambda r: -r[0]):
    print("%7.0f %-14s %s" % (tot, nm, top))
