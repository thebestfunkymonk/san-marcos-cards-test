import sys; sys.path.insert(0,".")
import shapely
from deck.motifs import fauna as FA, core as C, lion as L
from inkkit import geom as G
def areas(f):
    po = G.to_shape(f.outline(), tol=0.05).area
    sh = shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05).buffer(0) for m in f.marks if m.d]).area
    return po, sh
d = FA.fountain_darter(375, 525, 100, rot=210)
for i, m in enumerate(d.marks):
    print(i, m.kind, m.role, m.w, m.cap, m.join, len(m.d))
# drop each mark and see if mismatch disappears
for i in range(len(d.marks)):
    f = C.Frag([m for j, m in enumerate(d.marks) if j != i])
    po, sh = areas(f)
    if abs(po - sh) < 5: print("mismatch disappears when dropping mark", i, d.marks[i].role)
# single-mark self check (skia simplify of one stroke)
for i, m in enumerate(d.marks):
    f = C.Frag([m]); po, sh = areas(f)
    if abs(po-sh) > 2: print("single mark wrong", i, m.role, po, sh)
