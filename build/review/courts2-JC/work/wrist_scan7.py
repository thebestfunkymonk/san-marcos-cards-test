import sys, warnings, itertools, math; sys.path.insert(0,'.'); sys.path.insert(0,'art')
warnings.simplefilter('ignore')
from deck import courtkit as K
import JC, _jc_body as B
import numpy as np
from shapely.geometry import Point, LineString
res = []
grid = [[float(a) for a in s.split(',')] for s in sys.argv[1:6]]
torso = B.region(*JC.TORSO)
win = K.box(470, 380, 531, 480)
bl = B.reed_belt(torso, y=440.0, h=24.0, sag=4.0, x0=220.0, x1=560.0, front=358.0, rise=JC.BELT_RISE)
bpts = np.asarray(bl.shape.exterior.coords)
tl = LineString(sorted([tuple(p) for p in bpts if 470 < p[0] < 540 and p[1] < 438], key=lambda q: q[0]))
bb = LineString(sorted([tuple(p) for p in bpts if 470 < p[0] < 540 and p[1] > 440], key=lambda q: q[0]))
for fy, bend, dist, jx, bx in itertools.product(*grid):
    JC.JERK_R_LOW = [(512, 540), (jx + 6, 470), (jx, 428)]
    jer = B.region(*JC.jerk()).intersection(torso)
    spec = {**JC.SLEEVE_R_SPEC, "base": (bx, 552.0)}
    ww = spec['wrist_w']
    F=(548.0, fy)
    WR = np.array(K.fist_wrist(F, -90.0, bend=bend, dist=dist, **JC.FIST_KW))
    Bp = np.array(spec['base']); u = (WR - Bp)/np.hypot(*(WR-Bp)); n = np.array([u[1], -u[0]])
    wl, wr = WR + n*ww/2, WR - n*ww/2
    cl, cr = wl - u*spec['cuff'], wr - u*spec['cuff']
    sc = K.Scene(rank='J')
    sl, cf = K.sleeve(K.SleeveSpec(wrist=tuple(WR), folds=0, **spec))
    sc.part('sleeveR', sl); sc.part('cuffR', cf)
    h = K.fist(F, -90.0, wrist=tuple(WR), wrist_w=26.0, hand='L', **JC.FIST_KW).tucked(sc)
    front = K.U(h.shape, sl.shape, cf.shape)
    jl = jer.boundary.intersection(win).difference(front.buffer(0.5))   # visible jerkin edge
    ds = {}
    for c, p in {'wl': wl, 'cl': cl}.items():
        for nm, l in (('btop', tl), ('bbot', bb), ('jerk', jl)):
            ds[f'{c}-{nm}'] = l.distance(Point(*p)) if not l.is_empty else 99.0
    # the visible jerkin edge must end on the hand contour square-ish: distance from its end to cuff corners
    worst = min(ds.values())
    res.append((round(worst,1), fy, bend, dist, jx, bx, WR.round(1).tolist(), {k: round(v,1) for k, v in ds.items() if v < 7}))
res.sort(key=lambda r: -r[0])
for r in res[:16]: print(r)
