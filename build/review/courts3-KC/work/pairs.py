"""List near-miss pairs (as heal sees them) involving robe lines, before heal.
usage: pairs.py '<opts json>' [x0 y0 x1 y1]"""
import sys; sys.path.insert(0,'.')
import json, numpy as np, shapely
from deck import courtkit as K
from deck.motifs import core as C
from deck import frames as F
from art import KC
opts = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
box = tuple(map(float, sys.argv[2:6])) if len(sys.argv) >= 6 else (139, 55, 611, 525)
sc = KC.figure(opts)
res = sc.compose(heal_gaps=False)
band = C.stroke(f"M100 511L650 511", K.FINE, style="rule", role="_band")
res = res + band
marks = list(res.marks)
outl = {i: K.R(K.G.from_skia(m.skia())) for i, m in enumerate(marks) if m.d}
pieces = []
for grp in K._groups(marks):
    u = shapely.union_all([outl[i] for i in grp if i in outl])
    for pg in K._polys_of(u):
        if pg.area <= 0.05: continue
        mem = [i for i in grp if outl[i].intersects(pg)]
        pieces.append((pg, mem))
bx = shapely.box(*box)
geoms = [p[0] for p in pieces]
tree = shapely.STRtree(geoms)
pa_, pb_ = tree.query(geoms, predicate="dwithin", distance=K.GAP)
from shapely.ops import nearest_points
for a, b in zip(pa_, pb_):
    if a >= b: continue
    A, B = pieces[a], pieces[b]
    d = A[0].distance(B[0])
    if d < 0.08: continue
    ka = {marks[i].kind for i in A[1]}; kb = {marks[i].kind for i in B[1]}
    la = {marks[i].layer for i in A[1]}; lb = {marks[i].layer for i in B[1]}
    both_fill = ka == {"fill"} and kb == {"fill"} and la == lb
    need = K.GAP_FILL if both_fill else K.GAP_MARK
    if "stroke" in ka and "stroke" in kb and d >= K.GAP_MARK - 0.08:
        if K._run_len(A[0], B[0]) >= K.PAR_RUN - 0.5: need = K.GAP
        else: continue
    if d >= need - 0.08: continue
    p, q = nearest_points(A[0], B[0])
    if not bx.contains(p): continue
    ra = sorted({(marks[i].role or marks[i].kind).split('@')[0] for i in A[1]})
    rb = sorted({(marks[i].role or marks[i].kind).split('@')[0] for i in B[1]})
    print(f"{d:5.2f}<{need} at ({p.x:.1f},{p.y:.1f}) {ra[:4]} {la} | {rb[:4]} {lb}")
