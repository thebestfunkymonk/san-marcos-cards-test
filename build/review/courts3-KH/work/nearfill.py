import sys; sys.path.insert(0,'.')
from art import KH
from deck import courtkit as K
from inkkit import geom as G
import shapely, shapely.ops
from shapely.geometry import Point
import deck.courtkit as KK
cap = {}
orig = KK.heal
def h2(f, **kw):
    cap['f'] = f
    return orig(f, **kw)
KK.heal = h2
sc = KH.figure(); res = sc.compose()
f = cap['f']; marks = list(f.marks)
outl = {i: K.R(G.from_skia(m.skia())) for i, m in enumerate(marks) if m.d}
pieces = []
for grp in KK._groups(marks):
    u = shapely.union_all([outl[i] for i in grp if i in outl])
    for pg in KK._polys_of(u):
        if pg.area <= 0.05: continue
        mem = [i for i in grp if outl[i].intersects(pg)]
        pieces.append((pg, mem))
for pg, mem in pieces:
    roles = {marks[i].role for i in mem}
    if not ({'finger','thumb'} & roles): continue
    for qg, qm in pieces:
        d = pg.distance(qg)
        if 0.08 < d < 3.0 - 0.08 and marks[qm[0]].kind == 'fill':
            a, b = shapely.ops.nearest_points(pg, qg)
            print('hand piece', round(pg.representative_point().x), 'near fill', marks[qm[0]].layer, round(d,2), 'area', round(qg.area,2), (round(a.x,2), round(a.y,2)), (round(b.x,2), round(b.y,2)), [round(v,2) for v in qg.bounds])
