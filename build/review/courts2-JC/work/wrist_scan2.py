import sys, warnings, itertools; sys.path.insert(0,'.'); sys.path.insert(0,'art')
warnings.simplefilter('ignore')
from deck import courtkit as K
import JC, _jc_body as B
import numpy as np
from shapely.geometry import Point, LineString
torso = B.region(*JC.TORSO)
jer = B.region(*JC.JERK).intersection(torso)
bl = B.reed_belt(torso, y=440.0, h=24.0, sag=4.0, x0=220.0, x1=560.0, front=358.0)
win = K.box(470, 380, 533, 480)
lines = {'belt': bl.shape.boundary.intersection(win), 'jerk': jer.boundary.intersection(win)}
spec = JC.SLEEVE_R_SPEC
res = []
for fy, bend, dist, ww in itertools.product(*[[float(a) for a in s.split(',')] for s in sys.argv[1:5]]):
    F=(548.0, fy)
    WR = np.array(K.fist_wrist(F, -90.0, bend=bend, dist=dist, **JC.FIST_KW))
    Bp = np.array(spec['base']); u = (WR - Bp)/np.hypot(*(WR-Bp)); n = np.array([u[1], -u[0]])
    wl, wr = WR + n*ww/2, WR - n*ww/2
    cl, cr = wl - u*spec['cuff'], wr - u*spec['cuff']
    corners = {'wl': wl, 'wr': wr, 'cl': cl, 'cr': cr}
    ds = {f"{c}-{l}": lines[l].distance(Point(*p)) for c, p in corners.items() for l in lines}
    worst = min(ds.values())
    res.append((worst, fy, bend, dist, ww, WR.round(1), {k: round(v,1) for k, v in ds.items() if v < 8}))
res.sort(key=lambda r: -r[0])
for r in res[:15]: print(r)
