import sys
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
import numpy as np
from deck import courtkit as K
import art.QS as Q
from art import _qs_parts as QP
posy = Q.posy_parts()
handL = K.fist(Q.FIST_L, Q.POSY["axis_deg"], wrist=Q.WRIST_L, wrist_w=24.0, hand="R", **Q.HAND_L)
front = K.U(posy["holder"].shape, posy["leaves"].shape, posy["raceme"].shape, handL.hand.shape)
fr = QP.rot_geom(front.buffer(K.HALO, quad_segs=8), -Q.TILT, Q.PIVOT)
for f in (None, fr):
    hg = Q.head_group(front=f)
    lf = hg['lf']
    vis = lf.meta['vis']
    print('vis bounds', [round(v,1) for v in vis.bounds], 'area', round(vis.area))
    for m in lf.lines.marks:
        if m.role in ('current','terminal'):
            from inkkit import geom as G
            sh = G.to_shape(m.d, tol=0.1) if m.kind=='fill' else None
            print(' ', m.role, m.kind, m.d[:60])
# detail
from shapely.geometry import LineString, Point
from inkkit import geom as G
from art import _qs_body as B
hg0 = Q.head_group()
fc = QF = None
reg, po, pi = B.ribbon(Q.HAIR_F_OUT, Q.HAIR_F_IN)
vis = hg0['lf'].meta['vis']
fit = vis.difference(fr)
print('fit pieces', [ (round(g.area), [round(b) for b in g.bounds]) for g in K._polys_of(fit)])
cv = G.Curve(np.asarray(po, float))
for k in range(2):
    off = cv.offset(+1 * (K.MEDIUM/2 + K.GAP + K.FINE/2 + 0.2 + k * K.PITCH), spacing=0.5)
    ln = LineString(off)
    pcs = K._lines_of(ln.intersection(fit))
    print(k, [(round(g.length), [round(c) for c in g.coords[0]], [round(c) for c in g.coords[-1]]) for g in pcs])
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6,10))
for g in K._polys_of(vis):
    x,y = g.exterior.xy; ax.fill(x,y,color='goldenrod',alpha=.5)
for g in K._polys_of(fr):
    x,y = g.exterior.xy; ax.plot(x,y,'g-')
for k in range(2):
    off = cv.offset(+1 * (K.MEDIUM/2 + K.GAP + K.FINE/2 + 0.2 + k * K.PITCH), spacing=0.5)
    ax.plot(off[:,0], off[:,1], 'k-')
ax.set_xlim(290,380); ax.set_ylim(430,200); ax.set_aspect('equal')
plt.savefig('/home/luke/Projects/design/san-marcos-deck/build/review/courts2-QS/work/lockdbg.png', dpi=80)
