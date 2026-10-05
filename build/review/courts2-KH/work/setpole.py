import numpy as np
def setpole(KH, K, fist, topx, rbend=55.0, rdist=0.7):
    KH.FIST = tuple(fist); KH.POLE_TOP = (topx, 55.0)
    KH.POLE_DEG = float(np.degrees(np.arctan2(KH.POLE_TOP[1] - KH.FIST[1], KH.POLE_TOP[0] - KH.FIST[0])))
    W, B = KH._arm(KH.FIST, KH.POLE_DEG, KH.HAND_R, rbend, rdist)
    KH.WR = W; KH.WRISTS = (KH.WL, W); KH.SLEEVE_R = dict(KH.SLEEVE_R, base=B)
