import sys; sys.path.insert(0,'.')
import numpy as np, json
from shapely.geometry import Point, LineString
from deck import courtkit as K
from art import KC
sc = KC.figure({"robe":{"flute_kw":{"vy":-400.0,"widths":[34.0,10.0],"centre":30.0,"skip":[]}},"pockets":False})
items = {it.name: it for it in sc.items}
print(list(items))
def rayx(X, y, vy=-400.0): return 375 + X*(y-vy)/(511-vy)
stole = items['stole1'].occ
collar = items['collar'].occ
robe = items['robe'].occ
# stole outer edge on the right: for y in range, the min x of the stole at that y
for y in range(330, 420, 4):
    hl = LineString([(375,y),(620,y)])
    s = hl.intersection(stole)
    c = hl.intersection(collar)
    sx = max([g.bounds[2] for g in getattr(s,'geoms',[s]) if not g.is_empty], default=None)
    cx = max([g.bounds[2] for g in getattr(c,'geoms',[c]) if not g.is_empty], default=None)
    print(y, 'stole_edge %.1f' % sx if sx else None, 'collar_right %.1f'%cx if cx else None, ' rays', ' '.join('%d:%.1f'%(X, rayx(X,y)) for X in (103,108,113,118,123)))
print('collar bottom (right side)')
for x in range(440, 500, 3):
    vl = LineString([(x,250),(x,420)])
    c = vl.intersection(collar)
    ys = [g.bounds[3] for g in getattr(c,'geoms',[c]) if not g.is_empty]
    s = vl.intersection(stole)
    print(x, 'collar_bot %.1f' % max(ys) if ys else None)
# robe seam/inner top boundary
inner = robe  # 
