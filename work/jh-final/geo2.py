import sys; sys.path.insert(0,'.')
import numpy as np, shapely
from art import JH as M
from art import _jh_face as JF
from deck import courtkit as K
fc = JF.minstrel_profile(M.HEAD, brow_dy=-16.0, brow_sag=3.0, nostril=(7.5, 0.6, -80.0, 3.4, 160.0))
rot = lambda v: tuple(round(c,1) for c in shapely.affinity.rotate(shapely.Point(*v), M.TILT, origin=M.PIVOT).coords[0])
for k in ('chin','under_chin','throat','neck_front','ear'):
    print(k, rot(fc.anchors[k]))
sk = shapely.affinity.rotate(fc.skin, M.TILT, origin=M.PIVOT)
for y in range(256, 300, 2):
    s = sk.intersection(K.box(0,y,800,y+0.5))
    if not s.is_empty: print(y, round(s.bounds[0],1))
