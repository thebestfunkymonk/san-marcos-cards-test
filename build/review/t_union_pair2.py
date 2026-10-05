from rv import *
from deck.motifs import *
from inkkit import geom as G
import shapely, numpy as np, pathops
f=fountain_darter(0,0,100,facing=1,rot=345)
sp=[m for m in f.marks if m.role=="spine"][0]
mb=[m for m in f.marks if m.role=="membrane"][0]
print(sp.cap, sp.join, sp.miter, mb.cap, mb.join, mb.miter)
u = pathops.op(sp.skia(), mb.skia(), pathops.PathOp.UNION, fix_winding=True)
d = G.from_skia(u)
print("contours", d.count("M"))
Path = __import__("pathlib").Path
from deck.motifs.core import fill
fr = fill(d, color=T.INK)
save(fr, "pair_union_fill", zoom=10)
save(Frag([sp,mb]), "pair_line", zoom=10)
# shapely vs pathops
s = G.to_shape(d, tol=0.02)
print("to_shape valid", s.is_valid, s.area)
# raster area with rsvg: compare nonzero rendering
