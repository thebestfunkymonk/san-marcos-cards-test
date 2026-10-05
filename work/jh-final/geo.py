import sys; sys.path.insert(0,'.')
import numpy as np, shapely
from art import JH as M
from art import _jh_face as JF
from deck import courtkit as K
fc = JF.minstrel_profile(M.HEAD, brow_dy=-16.0, brow_sag=3.0, nostril=(7.5, 0.6, -80.0, 3.4, 160.0))
for k in ('eye','mouth_y','chin','throat','neck_front','ear','nape','neck_y'):
    v = fc.anchors[k]
    if isinstance(v, np.ndarray):
        r = shapely.affinity.rotate(shapely.Point(*v), M.TILT, origin=M.PIVOT)
        print(k, v.round(1), '-> tilted', (round(r.x,1), round(r.y,1)))
    else: print(k, v)
sk = shapely.affinity.rotate(fc.skin, M.TILT, origin=M.PIVOT)
# contour x-extent per row
for y in range(250, 300, 2):
    s = sk.intersection(K.box(0,y,800,y+0.5))
    if not s.is_empty: print(y, round(s.bounds[0],1), round(s.bounds[2],1))
c = M.JP.collar(M.H((367, 279)), M.H((425, 273)), M.H((361, 308)), M.H((431, 302)), bot_sag=5.0)
print('collar', [round(v,1) for v in c.shape.bounds])
