from rv import *
from deck.motifs import *
from inkkit import geom as G
import numpy as np, shapely
s = blind_salamander(0,0,radius=34, rot=20)
bb=np.array([G.bbox(G.from_skia(m.skia())) for m in s.marks])
print("outline bbox", [round(v,1) for v in s.bbox()])
print("true bbox", bb[:,0].min().round(1), bb[:,1].min().round(1), bb[:,2].max().round(1), bb[:,3].max().round(1))
ref = shapely.union_all([G.to_shape(G.from_skia(m.skia()),tol=0.05) for m in s.marks]).area
print("area", s.shape().area, ref)
x0,y0,x1,y1 = bb[:,0].min(), bb[:,1].min(), bb[:,2].max(), bb[:,3].max()
save(s, "sal_r34_line_full", view=(x0-8,y0-8,x1+8,y1+8), zoom=5)
save(s, "sal_r34_ko_full", view=(x0-8,y0-8,x1+8,y1+8), zoom=5, flood=T.JADE)
