"""cmp3.py <ID>: marks whose QA stroke outline differs from the skia outline (closed-ring miter spikes)."""
import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")
from deck import build as B, qa as QA
from deck.motifs import core as C
mod = B.load_art(sys.argv[1])
sc = mod.figure()
sc = sc[0] if isinstance(sc, tuple) else sc
res = sc.compose()
n = 0
for i, m in enumerate(res.marks):
    if m.kind != "stroke" or not m.d:
        continue
    a = C.Frag([m]).shape()
    b = QA._stroke_geom(m.d, m.w, m.cap, m.join, m.miter)
    if b is None:
        continue
    extra = b.difference(a.buffer(0.2))
    if extra.area > 0.5:
        n += 1
        c = extra.centroid
        print(i, m.role, m.w, m.join, m.miter, "extra area %.1f at (%.1f,%.1f)" % (extra.area, c.x, c.y))
print("total", n)
