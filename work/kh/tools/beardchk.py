import sys; sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck')
import numpy as np, shapely
from deck import courtkit as K
from deck.motifs import core as C
from inkkit import geom as G
import art._kh_head as KHH, art.KH as KH
locks = eval(sys.argv[1]) if len(sys.argv) > 1 else KH.BEARD_LOCKS["locks"]
fc = K.face(KH.HEAD, "frontal", **KH.FACE_KW)
mo = KHH.moustache(fc, KH.MOUSTACHE)
p = KHH.lobe_beard(fc, KH.BEARD, mo=mo, lines={"mode": "manual", "locks": locks})
marks = [m for m in p.lines.marks if m.role in ("current", "terminal")]
geoms = [K.R(G.from_skia(m.skia())) for m in marks]
ol = K.R(G.from_skia(C.stroke(K.D(p.shape.boundary.buffer(0.01)) if False else "", 1).skia())) if False else None
edge = p.shape.boundary.buffer(K.MEDIUM / 2)
cy = 207.0
for i, (m, g) in enumerate(zip(marks, geoms)):
    c = g.centroid
    others = [geoms[j] for j in range(len(geoms)) if j != i and not geoms[j].intersects(g)]
    dmin = min((g.distance(o) for o in others), default=99)
    print(f"{m.role:9s} at ({c.x-375:6.1f},{c.y-cy:6.1f})  to others {dmin:5.2f}  to edge {g.distance(edge):5.2f}")
