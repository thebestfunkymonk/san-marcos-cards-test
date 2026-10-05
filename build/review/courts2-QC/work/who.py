import sys, os
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import QC
from deck import courtkit as K
from deck.motifs import core as C
from inkkit import geom as G
import shapely
x0, y0, x1, y1 = map(float, sys.argv[1].split(','))
zone = shapely.box(x0, y0, x1, y1)
sc, fc = QC.figure()
res = QC.Q.compose(sc)
for m in res.marks:
    if m.layer != 'ink' and len(sys.argv) < 3: continue
    try:
        g = K.R(G.from_skia(m.skia()))
    except Exception:
        continue
    if g.intersects(zone):
        print(m.kind, m.role, m.w, m.layer, round(g.intersection(zone).area, 2), m.d[:120])
