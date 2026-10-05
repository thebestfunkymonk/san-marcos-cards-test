import numpy as np
def setchal(KH, K, x):
    KH.CHAL_X = x
    KH.GRIP_L = (x, KH.GRIP_L[1])
    (WL, BL) = KH._arm(KH.GRIP_L, -90.0, KH.HAND_L, 45.0, 1.10)
    KH.WL = WL; KH.ARM_L_BASE = BL; KH.WRISTS = (WL, KH.WRISTS[1]); KH.SLEEVE_L = dict(KH.SLEEVE_L, base=BL)
