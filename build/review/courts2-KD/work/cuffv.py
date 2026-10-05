import sys, warnings, itertools
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np
from art import KD
from art import _kd_body as B
from deck import courtkit as K
su = (np.array(KD.SASH[1]) - np.array(KD.SASH[0])); su = su/np.hypot(*su); sn = np.array([su[1], -su[0]])
grip = np.array(KD.SASH[0]) + su*KD.GRIP_T - sn*(KD.SASH_W/2 - KD.GRIP_IN)
fkw = dict(shaft_w=KD.GRIP_W, back=-1, h=KD.FIST["h"], reach=KD.FIST["reach"], knuckle=KD.FIST["knuckle"])
WL = K.fist_wrist(tuple(grip), KD.GRIP_AXIS, **KD.WRIST_L, **fkw)
print('WL', WL)
for BLx, depth, flare in itertools.product((222, 232, 242), (36, 40, 42, 44), (46,)):
    BL = np.array((BLx, 552.0))
    u = (WL - BL)/np.hypot(*(WL-BL)); nrm = np.array([u[1], -u[0]])
    B_ = WL - u*depth
    b0, b1 = B_ + nrm*flare/2, B_ - nrm*flare/2
    v = max((b0, b1), key=lambda p: p[1])
    print(BLx, depth, flare, 'vertex', np.round(v,1), 'other', np.round(min((b0,b1), key=lambda p:p[1]),1))
