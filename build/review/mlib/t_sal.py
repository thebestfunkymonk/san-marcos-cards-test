from rh import *
from deck.motifs import fauna as FA
from inkkit import geom as G
f = FA.blind_salamander(375, 525)
show(f, "sal-seal-4x", zoom=4, ground=T.RED)
x0,y0,x1,y1 = f.bbox(); print("seal size bbox", round(x1-x0,1), round(y1-y0,1), "L", round(f.meta['length'],1))
# Q♠ mirror: Ø110 frame, salamander must fit inside (≈ Ø 90 field)
for r in (34, 30):
    g = FA.blind_salamander(0, 0, radius=r)
    x0,y0,x1,y1 = g.bbox(); print("radius", r, "bbox", round(x1-x0,1), round(y1-y0,1), "warnings", g.meta.get("warnings"))
g = FA.blind_salamander(0, 0, radius=30, color=T.PAPER)
from deck.motifs import forms as FM
ts = FM.tight_spots(g, 4.2); print("r30 tight ground area", round(ts['area'],1))
circ = G.circle_d(0,0,50)
show(g, "sal-r30-mirror-ko-8x", zoom=8, flood=T.JADE, flood_d=circ, view=(-55,-55,55,55))
ko = C.knockout(circ, g)
rep = C.knockout_report(circ, ko, min_line=2.5, min_gap=3.0)
print({k: round(v,4) for k,v in rep.items()})
rep = C.knockout_report(G.circle_d(375,525,115), C.knockout(G.circle_d(375,525,115), f), min_line=2.5, min_gap=3.0)
print("seal-size ko", {k: round(v,4) for k,v in rep.items()})
