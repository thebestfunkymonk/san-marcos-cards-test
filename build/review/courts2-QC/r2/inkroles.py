"""ink area (px², top half, art window, visible = ink layer is on top) per mark role"""
import sys, collections
sys.path.insert(0, "art"); sys.path.insert(0, ".")
import QC
from deck import courtkit as K
from deck.motifs import core as C
from inkkit import geom as G
import shapely
for a in sys.argv[1:]:
    k, v = a.split("=", 1); QC.PACK[k] = eval(v)
sc, fc = QC.figure()
fr = QC.compose_scene(sc)
win = shapely.box(139, 55, 611, 505)
acc = collections.defaultdict(list)
for m in fr.marks:
    if m.layer != "ink" or not m.d:
        continue
    for pts, closed in G.as_polys(m.d, 0.3):
        if len(pts) < 2: continue
        if m.kind == "stroke":
            g = (shapely.LinearRing(pts) if closed and len(pts) > 2 else shapely.LineString(pts)).buffer(m.w / 2, quad_segs=4)
        else:
            if len(pts) < 3: continue
            g = shapely.Polygon(pts).buffer(0)
        acc[(m.role or "?", m.kind, m.w)].append(g)
tot = shapely.union_all([g for v in acc.values() for g in v]).intersection(win).area
tex = [g for k, v in acc.items() if k[0] in ("leaf", "midrib", "hatch") for g in v]
L_ = shapely.union_all(tex).intersection(win)
print("textile left %.0f right %.0f" % (L_.intersection(shapely.box(0,0,375,999)).area, L_.intersection(shapely.box(375,0,999,999)).area))
print("total ink top-half window %.0f px² (window %.0f) = %.2f%%" % (tot, win.area, 100 * tot / win.area))
rows = []
for k, v in acc.items():
    a = shapely.union_all(v).intersection(win).area
    rows.append((a, k))
for a, k in sorted(rows, reverse=True)[:30]:
    print("%7.0f  %5.2f%%  %s" % (a, 100 * a / win.area, k))
