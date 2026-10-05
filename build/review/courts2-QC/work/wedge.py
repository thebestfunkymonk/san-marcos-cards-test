import sys, os
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import QC
from deck import courtkit as K
import shapely
gshape, top = QC.Q.gown_outline(**QC.GOWN)
def test(plumes, tag):
    parts = dict(QC.FN.fan(QC.FIST_L, QC.FAN_AXIS, plumes, **QC.FAN_KW))
    pl = K.U(*[parts[f'plume{i}'].shape for i in range(len(plumes))], parts['ferrule'].shape)
    zone = shapely.box(150, 250, 270, 380)
    vis = gshape.intersection(zone).difference(pl)
    # narrow wedges: visible gown pieces inside the plume union's closing
    clo = pl.buffer(6).buffer(-6)
    wedge = vis.intersection(clo)
    pieces = [(round(g.area,1), [round(v,1) for v in g.bounds]) for g in K._polys_of(wedge) if g.area > 0.5]
    print(tag, 'visible gown in fan zone', round(vis.area,1), 'in wedges', pieces)
test(QC.PLUMES, 'base')
P = list(QC.PLUMES)
for h0 in (-164.0, -162.0, -168.0):
    q = list(P); q[0] = (h0,) + tuple(P[0][1:]); test(tuple(q), f'p0 heading {h0}')
for w in (27.0, 29.0):
    q = list(P); q[1] = tuple(P[1][:3]) + (w,); test(tuple(q), f'p1 w {w}')
for w in (25.0, 27.0):
    q = list(P); q[0] = tuple(P[0][:3]) + (w,); test(tuple(q), f'p0 w {w}')
