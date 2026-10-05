from rv import *
from deck.motifs import *
from deck.motifs import fauna
d = fountain_darter(0, 0, 100)
print(d.meta, len(d.marks))
save(d, "darter100", zoom=8)
x0,y0,x1,y1 = d.bbox(); print("bbox", x0,y0,x1,y1, "w", x1-x0, "h", y1-y0)
# body depth check
import numpy as np
from deck.motifs.forms import arc_spline
D = fauna.DARTER
prof = D["ventral"] + [D["nose"]] + D["dorsal"]
_, pts, _ = arc_spline(prof, headings={len(D["ventral"]): -90.0})
print("body depth max", pts[:,1].max()-pts[:,1].min(), "len (body only)", pts[:,0].max()-pts[:,0].min())
# roles
from collections import Counter
print(Counter(m.role for m in d.marks))
