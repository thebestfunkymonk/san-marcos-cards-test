from rv import *
from deck.motifs import *
from deck.motifs.core import circle_d, vesica_d, split_region
from inkkit import geom as G
import numpy as np
# two interlocked rings, chain-link: A over B at one crossing, B over A at the other
A = stroke(circle_d(0,0,30), T.MEDIUM); B = stroke(circle_d(40,0,30), T.MEDIUM)
from shapely.geometry import box
left = box(-100,-100,20,100); right = box(20,-100,100,100)
# A over B on the top crossing, B over A on the bottom crossing
top = box(-100,-100,100,0); bot = box(-100,0,100,100)
A_top = clip(A, top); A_bot = clip(A, bot); B_top = clip(B, top); B_bot=clip(B, bot)
chain = interlace(B_top, A_top) + interlace(A_bot, B_bot)
save(chain, "interlace_chain", zoom=6)
# measure clear gap
for under, over in ((cut(B_top, A_top), A_top), (cut(A_bot, B_bot), B_bot)):
    print("clear under->over", round(under.shape().distance(over.shape()),2))
# half-hatch a new shape: a pecan-ish leaflet on an S midrib and a shield split by a line
leaf_d = vesica_d((0,0),(0,-90),30)
mid = "M0 0 C 6 -30 -6 -60 0 -90"
hh = half_hatch(leaf_d, mid, "perp", side=1)
f = stroke(leaf_d, style="point") + stroke(mid) + hh
save(f, "halfhatch_leaf_S", zoom=6)
# check hatch pitch & butt termination on the midrib (distance of hatch ends to the midrib centreline)
from shapely.geometry import LineString
mpts = G.flatten(mid, 0.05)[0][0]; ml = LineString(mpts)
lp = G.flatten(leaf_d,0.05)[0][0]; ll = LineString(lp)
ends=[]
for m in hh.marks:
    for p,c in G.flatten(m.d,0.01):
        a,b = p[0],p[-1]
        from shapely.geometry import Point
        da = min(ml.distance(Point(a)), ll.distance(Point(a))); db = min(ml.distance(Point(b)), ll.distance(Point(b)))
        ends += [da, db]
print("max hatch end offset from a contour/midrib centreline", round(max(ends),3), "n lines", len(ends)//2)
# rotated shield
shield = "M-40 -50 L40 -50 L40 10 A 40 40 0 0 1 -40 10 Z"
hh2 = half_hatch(shield, [(0,-60),(0,60)], -45, side=1)
save(stroke(shield, style="rule") + stroke("M0 -50 L0 50", style="rule") + hh2, "halfhatch_shield", zoom=5)
