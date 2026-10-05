import sys
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
import numpy as np
from shapely.geometry import LineString, Point
from inkkit import geom as G
from deck import courtkit as K
import art.QS as Q
from art import _qs_parts as QP, _qs_body as B
posy = Q.posy_parts()
handL = K.fist(Q.FIST_L, Q.POSY["axis_deg"], wrist=Q.WRIST_L, wrist_w=24.0, hand="R", **Q.HAND_L)
front = K.U(posy["holder"].shape, posy["leaves"].shape, posy["raceme"].shape, handL.hand.shape)
fr = QP.rot_geom(front.buffer(K.HALO, quad_segs=8), -Q.TILT, Q.PIVOT)
hg0 = Q.head_group()
vis = hg0['lf'].meta['vis']
reg, po, pi = B.ribbon(Q.HAIR_F_OUT, Q.HAIR_F_IN)
for R_ in (vis, vis.difference(fr)):
    tr = K.TD/2
    safe = R_.buffer(-(tr + K.GAP_MARK + K.MEDIUM / 2 + 0.1), quad_segs=12)
    cv = G.Curve(np.asarray(po, float))
    for k in range(2):
        off = cv.offset(+1 * (K.MEDIUM/2 + K.GAP + K.FINE/2 + 0.2 + k * K.PITCH), spacing=0.5)
        ln = LineString(off)
        pcs = [g for g in K._lines_of(ln.intersection(R_)) if g.length >= 10]
        s0 = [ln.project(Point(g.coords[0])) for g in pcs]
        piece = pcs[int(np.argmin(s0))]
        q = np.asarray(piece.coords)
        pc = G.Curve(q); Lp = pc.length
        ss = np.arange(0.0, Lp, 0.5)
        ins = np.array([safe.contains(Point(*pc.at_s(s))) for s in ss])
        runs = []
        cur = None
        for s, i in zip(ss, ins):
            if i and cur is None: cur = s
            if not i and cur is not None: runs.append((cur, s)); cur = None
        if cur is not None: runs.append((cur, Lp))
        print(k, 'Lp', round(Lp), 'safe runs', [(round(a), round(b), [round(c) for c in pc.at_s(b-0.5)]) for a, b in runs])
    print('---')
