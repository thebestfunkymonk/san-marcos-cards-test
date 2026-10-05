import sys
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
import numpy as np
from shapely.geometry import Point, LineString
from deck import courtkit as K
import art.QS as Q
from art import _qs_parts as QP
for base, W, sag, wd, ww in ((Q.SLEEVE_L, Q.WRIST_L, 6.0, 54.0, 32.0), (Q.SLEEVE_R, Q.WRIST_R, -6.0, 56.0, 34.0)):
    sl, cf = K.sleeve(K.SleeveSpec(base=base, wrist=W, sag=sag, width=wd, wrist_w=ww, cuff=14.0, folds=0))
    m = sl.meta
    print('W', np.round(m['W'],1), 'u', np.round(m['u'],3), 'n', np.round(m['n'],3), 'cuff bounds', np.round(cf.shape.bounds,1))
    print(' W in cuff?', cf.shape.contains(Point(*m['W'])), 'dist', round(cf.shape.distance(Point(*m['W'])),2))
    inner = sl.shape.buffer(-(K.MEDIUM/2 + K.GAP_MARK))
    for off in (-9, 0, 9):
        q = m['W'] + m['n']*off
        s = 0
        while not cf.shape.contains(Point(*(q - m['u']*s))) and s < 30: s += .25
        s1 = s
        while cf.shape.contains(Point(*(q - m['u']*s))) and s < 60: s += .25
        print('  off', off, 'enter', s1, 'exit', s, 'p0', np.round(q - m['u']*(s-2),1))
print('---- drips as built')
from inkkit import geom as G
for base, W, sag, wd, ww in ((Q.SLEEVE_L, Q.WRIST_L, 6.0, 54.0, 32.0), (Q.SLEEVE_R, Q.WRIST_R, -6.0, 56.0, 34.0)):
    sl, cf = K.sleeve(K.SleeveSpec(base=base, wrist=W, sag=sag, width=wd, wrist_w=ww, cuff=14.0, folds=0))
    part = QP.drip_fringe_ko(sl, cf)
    u = part.meta['u']
    for mk in part.meta['drips'].marks:
        if mk.role == 'drip':
            pts = G.as_polys(mk.d, 0.1)[0][0]
            p0, p1 = np.asarray(pts[0]), np.asarray(pts[-1])
            print(' p0', p0.round(1), 'p1', p1.round(1), 'p0.u', round(float(p0 @ u),1), 'p1.u', round(float(p1 @ u),1))
