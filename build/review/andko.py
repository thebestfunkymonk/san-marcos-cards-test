import sys; sys.path.insert(0,"build/review"); sys.path.insert(0,".")
from rend import out
import shapely
from deck import tokens as T
from deck.motifs import lion as L, core as C
from inkkit import geom as G
f = L.lion_andante(0,0)
po = G.to_shape(f.outline(), tol=0.05)
sh = shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05).buffer(0) for m in f.marks if m.d])
diff = po.symmetric_difference(sh)
print(diff.area, diff.bounds)
big = [g for g in getattr(diff,'geoms',[diff]) if g.area > 5]
for g in big: print(round(g.area,1), [round(v,1) for v in g.bounds])
out(f, "andante-ko-3x", (-170,-230,170,230), 2, flood=T.JADE)
