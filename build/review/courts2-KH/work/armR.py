# helper for experiments: set the right wrist + forearm along the wrist direction
import numpy as np
def setR(KH, K, bend, dist, L=110.0, width=46.0, wrist_w=36.0, cuff=15.0, sag=0.0, butt=None, turn=0.0):
    g = K.fist_geom(KH.FIST, KH.POLE_DEG, **KH.HAND_R)
    b = np.radians(bend)
    d = np.cos(b) * g['axis'] + np.sin(b) * g['down']
    W = g['Bs'] + g['hb'] * dist * d
    t = np.radians(turn)
    d2 = np.array([d[0]*np.cos(t) - d[1]*np.sin(t), d[0]*np.sin(t) + d[1]*np.cos(t)])
    KH.WRISTS = (KH.WRISTS[0], tuple(W))
    KH.ARM_R_BASE = tuple(W + L * d2)
    KH.ARM_R_SAG = sag
    KH.SLEEVE_R = dict(width=width, wrist_w=wrist_w, cuff=cuff)
    KH.POLE_BUTT = butt
    return W, KH.ARM_R_BASE

def setL(KH, K, bend, dist, L=110.0, width=None, wrist_w=None, cuff=None, sag=0.0, turn=0.0, base=None):
    g = K.fist_geom(KH.GRIP_L, -90.0, **KH.HAND_L)
    b = np.radians(bend)
    d = np.cos(b) * g['axis'] + np.sin(b) * g['down']
    W = g['Bs'] + g['hb'] * dist * d
    t = np.radians(turn)
    d2 = np.array([d[0]*np.cos(t) - d[1]*np.sin(t), d[0]*np.sin(t) + d[1]*np.cos(t)])
    KH.WRISTS = (tuple(W), KH.WRISTS[1])
    sl = dict(KH.SLEEVE_L)
    sl['base'] = tuple(W + L * d2) if base is None else base
    sl['sag'] = sag
    for k, v in (('width', width), ('wrist_w', wrist_w), ('cuff', cuff)):
        if v is not None: sl[k] = v
    KH.SLEEVE_L = sl
    return W, sl['base']
