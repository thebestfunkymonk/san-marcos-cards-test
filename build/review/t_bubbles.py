from rv import *
from deck.motifs import *
from inkkit import geom as G
import numpy as np
def sizes(f):
    out=[]
    for m in f.marks:
        if m.role=="bubble":
            x0,y0,x1,y1=G.bbox(m.d)
            out.append(round((x1-x0) + (m.w if m.kind=="stroke" else 0),2))
    return out
b = bubble_beading((115, 480), (115, 260), 4, n=9)
print("README A-spade column example sizes (outer):", sizes(b))
b2 = bubble_beading((115, 480), (115, 260), 4, n=9, ratio=3**(1/8), d_max=12)
print("with ratio 3^(1/8), d_max 12:", sizes(b2))
c = conduit("M375 480 L375 367", 12, n=5)
print("conduit 12, n=5 default sizes:", sizes(c), c.meta.get("warnings"))
c2 = conduit("M375 480 L375 367", 12, n=5, d_max=6)
print("conduit 12, n=5, d_max=6:", sizes(c2), c2.meta.get("warnings"))
