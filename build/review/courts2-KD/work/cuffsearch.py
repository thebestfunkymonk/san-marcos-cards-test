import sys, warnings, itertools
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np
from art import KD
from deck import courtkit as K
su = (np.array(KD.SASH[1]) - np.array(KD.SASH[0])); su = su/np.hypot(*su); sn = np.array([su[1], -su[0]])
fkw = dict(shaft_w=KD.GRIP_W, back=-1, h=KD.FIST["h"], reach=KD.FIST["reach"], knuckle=KD.FIST["knuckle"])
H = [(450,453),(459,462),(482,485)]
def clear(p):
    y = p[1]
    return min((0 if a <= y <= b else min(abs(y-a), abs(y-b))) for a, b in H)
res = []
for GT, bend, dist, BLx, depth, flare, width in itertools.product(range(110, 127, 2), (35,40,45,50,55), (0.62,0.67,0.72,0.77,0.82), (200,210,222,235,250), (34,36,38), (44,46,48), (34,36)):
    grip = np.array(KD.SASH[0]) + su*GT - sn*(KD.SASH_W/2 - KD.GRIP_IN)
    WL = K.fist_wrist(tuple(grip), KD.GRIP_AXIS, bend=bend, dist=dist, **fkw)
    BL = np.array((BLx, 552.0))
    u = (WL - BL)/np.hypot(*(WL-BL)); nrm = np.array([u[1], -u[0]])
    a0, a1 = WL + nrm*width/2, WL - nrm*width/2
    Bc = WL - u*depth
    b0, b1 = Bc + nrm*flare/2, Bc - nrm*flare/2
    cl = [clear(q) for q in (a1, b0, b1)]   # a0 = top-left under the hand? check all but the one inside the hand
    cl_all = [clear(q) for q in (a0, a1, b0, b1)]
    cost = abs(GT-115)/3 + abs(bend-45)/10 + abs(dist-0.72)/0.05 + abs(BLx-222)/15 + abs(depth-36)/2 + abs(flare-46)/2 + abs(width-36)/2
    res.append((min(cl), cost, GT, bend, dist, BLx, depth, flare, width, np.round(a0,1), np.round(a1,1), np.round(b0,1), np.round(b1,1), [round(c,1) for c in cl_all]))
good = [r for r in res if r[0] >= 6.0]
good.sort(key=lambda r: r[1])
for r in good[:25]: print(r[1:])
print(len(good))
