import sys, warnings, itertools
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np
from art import KD
from deck import courtkit as K
su = (np.array(KD.SASH[1]) - np.array(KD.SASH[0])); su = su/np.hypot(*su); sn = np.array([su[1], -su[0]])
fkw = dict(shaft_w=KD.GRIP_W, back=-1, h=KD.FIST["h"], reach=KD.FIST["reach"], knuckle=KD.FIST["knuckle"])
def bands(uc, st):
    yt = 482 - uc
    return [(yt-3-st-3, yt-3-st), (yt-3, yt), (482, 485)]
def clear(p, H):
    y = p[1]
    return min((-(min(y-a, b-y)) if a <= y <= b else min(abs(y-a), abs(y-b))) for a, b in H)
res = []
for GT, bend, dist, BLx, depth, flare, uc, st in itertools.product(range(108, 126, 1), (30,35,40,45,50,55,60), (0.62,0.67,0.72,0.77,0.82), range(170, 300, 10), (34,36,38), (42,44,46,48), (20,), (6,)):
    grip = np.array(KD.SASH[0]) + su*GT - sn*(KD.SASH_W/2 - KD.GRIP_IN)
    WL = K.fist_wrist(tuple(grip), KD.GRIP_AXIS, bend=bend, dist=dist, **fkw)
    BL = np.array((BLx, 552.0))
    u = (WL - BL)/np.hypot(*(WL-BL)); nrm = np.array([u[1], -u[0]])
    width = 36
    a0, a1 = WL + nrm*width/2, WL - nrm*width/2
    Bc = WL - u*depth
    b0, b1 = Bc + nrm*flare/2, Bc - nrm*flare/2
    H = bands(uc, st)
    cl = [clear(q, H) for q in (a1, b0, b1)]
    cost = abs(GT-115)/2 + abs(bend-45)/5 + abs(dist-0.72)/0.05 + abs(BLx-222)/10 + abs(depth-36)/1 + abs(flare-46)/1 + abs(uc-20)/1.5 + abs(st-6)/1
    res.append((round(min(cl),1), round(cost,1), GT, bend, dist, BLx, depth, flare, uc, st, [round(c,1) for c in cl]))
for thr in (6, 5, 4.5, 4):
    good = sorted([r for r in res if r[0] >= thr], key=lambda r: r[1])
    print('thr', thr, len(good))
    for r in good[:8]: print('  ', r)
print('best per GT')
for gt in range(108, 126):
    rr = sorted([r for r in res if r[2] == gt], key=lambda r: (-min(r[0], 6.0), r[1]))
    print(gt, rr[0])
