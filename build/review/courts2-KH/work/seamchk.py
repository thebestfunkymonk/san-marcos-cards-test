import sys, warnings; sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck'); warnings.simplefilter('ignore')
import numpy as np
from shapely.geometry import Point, LineString
import art.KH as KH
from art import _kh_parts as KP
from deck import courtkit as K
def corners(W, sl):
    B = np.asarray(sl['base']); W = np.asarray(W)
    u = (W - B) / np.hypot(*(W - B)); n = np.array([u[1], -u[0]])
    return W + n * sl['wrist_w'] / 2, W - n * sl['wrist_w'] / 2
def report(KH):
    robe_m, rip, inner = KP.robe(KH.ROBE, border=30.0, pitch=(96.0, 36.0), origin=(K.AX, 312.0))
    seam = inner.boundary
    lo, hi = KH._pole_line()
    pole = LineString([tuple(lo), tuple(hi)]).buffer(9, cap_style=2)
    chal = KP.chalice(KH.CHAL_X, KH.CHAL_RIM, rim_hw=29.0, bowl_h=44.0, stem_len=KH.CHAL_STEM, foot_hw=KH.CHAL_FOOT, tip_r=2.2)
    out = {}
    for nm, W, sl in (('L', KH.WRISTS[0], KH.SLEEVE_L), ('R', KH.WRISTS[1], KH.SLEEVE_R)):
        a, b = corners(W, sl)
        up, lw = (a, b) if a[1] < b[1] else (b, a)
        s_, c_ = K.sleeve(K.SleeveSpec(wrist=tuple(W), color=K.JADE, cuff_color=K.JADE, **sl))
        out[nm] = dict(upper=np.round(up, 1).tolist(), seam=round(seam.distance(Point(*up)), 1),
                       lower_seam=round(seam.distance(Point(*lw)), 1),
                       pole=round(pole.distance(Point(*lw)), 1) if nm == 'R' else None,
                       foot=round(chal.shape.distance(c_.shape), 1) if nm == 'L' else None)
    return out
if __name__ == '__main__':
    print(report(KH))
