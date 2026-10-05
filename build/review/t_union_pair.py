from rv import *
from deck.motifs import *
from inkkit import geom as G
import shapely, numpy as np, pathops
f=fountain_darter(0,0,100,facing=1,rot=345)
ms=[m for m in f.marks]
shp=[G.to_shape(G.from_skia(m.skia()),tol=0.02) for m in ms]
for i in range(len(ms)):
    for j in range(i+1,len(ms)):
        u = pathops.op(ms[i].skia(), ms[j].skia(), pathops.PathOp.UNION, fix_winding=True)
        a = G.to_shape(G.from_skia(u),tol=0.02).area
        r = shapely.union_all([shp[i],shp[j]]).area
        if abs(a-r)>0.02*r+0.5:
            print(i,ms[i].role,j,ms[j].role, round(a,1), round(r,1))
