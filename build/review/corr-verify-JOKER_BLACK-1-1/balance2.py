import os, sys
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "art"))
import shapely
from deck import tokens as T
import _joker_black_plumage as PL, _joker_black_props as PR, _joker_black_pose as P
legs, _ = PR.legs()
pl = PL.build(extra_solid=legs)
solid = pl["solid"].difference(PR.coronet_hull().buffer(T.INTERLACE_GAP))
cor = PR.coronet()
dx, dy = PR.FIG_SHIFT
jade = pl["jade"].shape()
bird = shapely.union_all([solid, pl["ink"].shape(), pl["gold"].shape(), jade])
rays = PR.call_rays().shape()
def fill_holes(g):
    return shapely.union_all([shapely.Polygon(p.exterior) for p in getattr(g, 'geoms', [g])])
for name, g in [('bird ink', bird), ('bird+cor ink', shapely.union_all([bird, cor])),
                ('bird+cor silhouette', fill_holes(shapely.union_all([bird, cor]))),
                ('bird+cor+rays ink', shapely.union_all([bird, cor, rays])),
                ('bird body only (y<wire)', bird.intersection(shapely.box(0,0,750,470)))]:
    q = g.centroid; b = g.bounds
    print(f"{name:26s} area {g.area:8.0f} centroid ({q.x+dx:6.1f},{q.y+dy:6.1f}) bbox x {b[0]+dx:.1f}-{b[2]+dx:.1f} (mid {(b[0]+b[2])/2+dx:.1f}) y {b[1]+dy:.1f}-{b[3]+dy:.1f}")
print('wire ends', PR.WIRE_L + [dx, dy], PR.WIRE_R + [dx, dy], 'kink', PR.KINK + [dx, dy])
print('bulbs card x', [x + dx for x in PR.BULB_X])
