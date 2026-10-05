from rh import *
import math
from deck.motifs import geometric as M
from deck.motifs import rice as RI
from deck.motifs import fauna as FA
from deck import frames as F
from inkkit import geom as G
heart = F.ace_pip_d('H')
print("heart bbox", [round(v,1) for v in G.bbox(heart)])
x0,y0,x1,y1 = G.bbox(heart)
ros = M.source_rosette(375, 540, 40, twist=False, w=T.MEDIUM)
print("A♥ rosette detail:", ros.meta['rosette']['detail'])
bub = C.bubble_row((375, 540-40-3.1-8), (375, y0+0.3*(y1-y0)), C.bubble_sizes(6.3, 5), w=T.MEDIUM)
ko = C.knockout(heart, ros, bub)
rep = C.knockout_report(heart, ko, min_line=2.5, min_gap=3.0)
print("A♥ KO:", {k: round(float(v),4) for k,v in rep.items()})
show(C.Frag(), "ah-ko-1x", zoom=1, view=(x0-10,y0-10,x1+10,y1+10), under=[(ko, T.RED)])
show(C.Frag(), "ah-ko-rosette-6x", zoom=6, view=(325,490,425,590), under=[(ko, T.RED)])
# odd-size rosettes: check tight spots
from deck.motifs import forms as FM
for R in (20, 33, 55, 75, 110, 150):
    for w in (T.FINE, T.MEDIUM):
        r = M.source_rosette(0,0,R, w=w)
        ts = FM.tight_spots(r, 4.2)
        print(f"rosette R{R} w{w}: detail {r.meta['rosette']['detail']}, ground<4.2 {ts['area']:.1f}px2, warnings {r.meta.get('warnings')}")
