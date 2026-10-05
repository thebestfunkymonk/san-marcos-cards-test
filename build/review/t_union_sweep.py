from rv import *
from deck.motifs import *
from deck.motifs import sheet, sheet_figurative
from inkkit import geom as G
import shapely, numpy as np
def ref(f): return shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05) for m in f.marks if m.d]).area
def bad(f):
    a=f.shape().area; r=ref(f); return abs(a-r)>0.01*r, a, r
specs = sheet.specimens()
for sp in specs:
    b,a,r = bad(sp["frag"])
    print(("BAD " if b else "ok  ")+sp["title"], round(a,1), round(r,1))
