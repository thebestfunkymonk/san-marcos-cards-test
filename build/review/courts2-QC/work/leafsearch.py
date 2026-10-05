import sys, os
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, '.')
import QC
from deck import courtkit as K
import shapely, numpy as np
cap = {}
orig = QC.GW.gown
def spy(shape, **kw):
    cap.update(kw); cap['shape'] = shape
    return orig(shape, **kw)
QC.GW.gown = spy
sc, fc = QC.figure()
soft = cap['soft']; pack = dict(cap['pack']); joins = pack.pop('no_show')
excl = cap['exclude']
shape = cap['shape']
inner = shape.buffer(-QC.GOWN_BORDER, quad_segs=16)
allowed = inner.buffer(-2.5).difference(K.R(excl))
tz = inner.buffer(-(3.0 + K.FINE / 2 + 0.3)).difference(K.R(excl).buffer(-1.2))
top = shapely.box(139, 55, 611, 511)
def run(**over):
    pk = dict(pack); pk.update(over)
    f, placed = QC.GW.leaf_pack(allowed, soft=soft, tip_zone=tz, **pk)
    vis_top = 0; bad = 0; n_top = 0
    for (b, L, W, bd, pg) in placed:
        v = pg.difference(soft).intersection(top)
        if v.area > 30: n_top += 1
        vis_top += v.area
        if v.intersects(joins): bad += 1
    return len(placed), n_top, round(vis_top), bad
print('current', run())
for dx in (-6, -4, -2, 2, 4, 6):
    for dy in (-4, 0, 4):
        o = (375.0 + dx, 330.0 + dy)
        print(o, run(origin=o))
