import sys; sys.path.insert(0,".")
import shapely
from deck.motifs import rice as R
f = R.rice_wreath_arc(0,0,150)
s = f.shape()
m = shapely.affinity.scale(s, -1, 1, origin=(0,0))
d = s.symmetric_difference(m)
print(round(d.area,1))
for g in sorted(getattr(d,'geoms',[d]), key=lambda g:-g.area)[:6]:
    print(round(g.area,1), [round(v,1) for v in g.bounds])
