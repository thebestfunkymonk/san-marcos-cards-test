import sys, os
sys.path.insert(0, '.'); sys.path.insert(0, 'art')
import numpy as np
from deck import courtkit as K
import JD, _jd_parts as J
T = J.Trumpet(JD.MOUTH, JD.AXIS)
FIST_R, _ = T.point_at_y(394.0)
WR = K.fist_wrist(FIST_R, JD.AXIS, bend=35.0, dist=0.85, shaft_w=18.0, back=+1, h=36.0)
print('FIST_R', FIST_R, 'WR', WR)
g = K.fist_geom(FIST_R, JD.AXIS, shaft_w=18.0, back=+1, h=36.0); print('geomR', {k: (np.round(v,1) if hasattr(v,'__len__') else round(v,2)) for k,v in g.items()})
HAND_L = dict(shaft_w=10.0, back=-1, h=34.0, reach=3.0)
WL = K.fist_wrist((269.0, 460.0), -90.0, bend=45.0, **HAND_L)
print('WL', WL)
g = K.fist_geom((269.0, 460.0), -90.0, **HAND_L); print('geomL', {k: (np.round(v,1) if hasattr(v,'__len__') else round(v,2)) for k,v in g.items()})
sc = JD.figure()
for n in ('cuffL', 'cuffR', 'forearmR', 'forearmL', 'handL', 'handR', 'map'):
    it = [i for i in sc.items if i.name == n][0]
    xy = np.asarray(it.occ.exterior.coords)
    print(n, 'n', len(xy))
    if n.startswith('cuff'):
        print(np.round(xy[::max(1, len(xy)//24)], 1).tolist())
