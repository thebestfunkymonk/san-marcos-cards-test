from rh import *
from deck.motifs import geometric as M
from deck.motifs import forms as FM
from inkkit import geom as G
from shapely.geometry import LineString
f1 = M.comb_spray("M0 0 A 40 40 0 0 1 60 -40", cone=8)
f2 = M.comb_spray("M100 0 A 25 25 0 0 1 130 -30")
show(f1 + f2, "comb-curved-6x", zoom=6)
# do ticks on the concave side cross or crowd each other?
for name, f in (("r40", f1), ("r25", f2)):
    ticks = [LineString(p) for m in f.marks if m.role == "tick" for p, _ in G.flatten(m.d)]
    cross = sum(1 for i in range(len(ticks)) for j in range(i+1, len(ticks)) if ticks[i].crosses(ticks[j]))
    mind = min(ticks[i].distance(ticks[j]) for i in range(len(ticks)) for j in range(i+1, len(ticks)) if not ticks[i].touches(ticks[j]) and ticks[i].distance(ticks[j]) > 0) if len(ticks) > 1 else None
    print(name, "ticks", len(ticks), "crossing pairs", cross, "min centreline distance between non-touching ticks", round(mind, 2) if mind else mind)
# running wave flow -1 == mirror of flow +1 about the band centre?
a = M.running_wave(0, 300, 0, rule=False)
b = M.running_wave(0, 300, 0, rule=False, flow=-1)
print("flow -1 vs mirror(flow +1) symdiff px2:", round(a.mirror_x(150).shape().symmetric_difference(b.shape()).area, 2))
c = M.running_wave(0, 300, 0, rule=False, up=1)
print("up +1 vs mirror_y symdiff px2:", round(a.mirror_y(0).shape().symmetric_difference(c.shape()).area, 2))
