import sys; sys.path.insert(0,'.')
import art.QH as Q
from deck import courtkit as K
from art import _qh_face as QF, _qh_cap as CP
fc = QF.queen_face(Q.HEAD, wing_mode="hook", wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)
print('head bounds', [round(v,1) for v in K.R(fc.head).bounds])
print('anchors', {k: v for k, v in fc.anchors.items()})
cap = CP.Cap(Q.CAP_C, Q.CAP_R, **Q.CAP_KW)
print('base', [round(v,1) for v in cap.base().shape.bounds])
r = cap.rim()
print('rim', [round(v,1) for v in r.shape.bounds])
import numpy as np
ext = np.asarray(r.shape.exterior.coords)
for x in range(310, 450, 10):
    ys = [p[1] for p in ext if abs(p[0]-x)<1.0]
    print(x, [round(y,1) for y in sorted(ys)][:2], [round(y,1) for y in sorted(ys)][-2:])
