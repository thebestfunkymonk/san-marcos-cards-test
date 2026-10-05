import sys, warnings, itertools
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np
from art import KD
from deck import courtkit as K
su = (np.array(KD.SASH[1]) - np.array(KD.SASH[0])); su = su/np.hypot(*su); sn = np.array([su[1], -su[0]])
fkw = dict(shaft_w=KD.GRIP_W, back=-1, h=KD.FIST["h"], reach=KD.FIST["reach"], knuckle=KD.FIST["knuckle"])
for GT, bend, dist, BLx, depth in itertools.product((118,120,122,124), (45,), (0.72,), (222,), (34,36,38)):
    grip = np.array(KD.SASH[0]) + su*GT - sn*(KD.SASH_W/2 - KD.GRIP_IN)
    WL = K.fist_wrist(tuple(grip), KD.GRIP_AXIS, bend=bend, dist=dist, **fkw)
    BL = np.array((BLx, 552.0))
    u = (WL - BL)/np.hypot(*(WL-BL)); nrm = np.array([u[1], -u[0]])
    B_ = WL - u*depth
    b0, b1 = B_ + nrm*23, B_ - nrm*23
    v = max((b0, b1), key=lambda p: p[1])
    ok = v[1] >= 491 or v[1] <= 476
    print(ok, GT, bend, dist, BLx, depth, 'WL', np.round(WL,1), 'vertex', np.round(v,1))
