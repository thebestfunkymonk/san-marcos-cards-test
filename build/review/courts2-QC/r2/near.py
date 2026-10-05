import sys
sys.path.insert(0, "art"); sys.path.insert(0, ".")
import QC, numpy as np, shapely
from inkkit import geom as G
x, y, r = map(float, sys.argv[1:4])
sc, fc = QC.figure()
fr = QC.compose_scene(sc)
P = shapely.Point(x, y).buffer(r)
for m in fr.marks:
    if not m.d: continue
    for pts, closed in G.as_polys(m.d, 0.3):
        if len(pts) < 2: continue
        ln = shapely.LineString(pts) if len(pts) > 1 else None
        if ln is not None and ln.intersects(P):
            pts = np.asarray(pts)
            # print local vertices near
            idx = [i for i, q in enumerate(pts) if np.hypot(q[0]-x, q[1]-y) < r * 1.5]
            print(m.layer, m.kind, m.w, m.role, "closed" if closed else "open", "n=%d" % len(pts),
                  "ends", np.round(pts[0], 1), np.round(pts[-1], 1), "near", [tuple(np.round(pts[i], 1)) for i in idx[:12]])
