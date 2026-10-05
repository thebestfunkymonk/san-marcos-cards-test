from rh import *
from deck.motifs import lion as LI
from deck.motifs import geometric as M
from inkkit import geom as G
from shapely.geometry import Point
a = LI.lion_andante(0, 0, clip_lens=True)
b = LI.lion_andante(0, 0, clip_lens=False)
geo = M.lens_geometry(0, -220, 220, 330)
lens = C.region(geo["d"]).buffer(-(2.1/2 + 4.2))
hb = b.select(lambda m: m.role in ("head",))
outside = hb.shape().difference(lens.buffer(1.05))
print("head ink outside clip zone (px^2):", round(outside.area,2), "bounds", [round(v,1) for v in outside.bounds] if not outside.is_empty else None)
lost = b.shape().difference(a.shape().buffer(0.3))
print("total ink removed by the lens clip (px^2):", round(lost.area,1))
for g in sorted(getattr(lost,'geoms',[lost]), key=lambda g:-g.area)[:6]:
    print("   piece", round(g.area,1), [round(v,1) for v in g.bounds])
show(b, "andante-head-noclip-8x", zoom=8, ground=T.BOARD, view=(-160,-130,-20,40))
