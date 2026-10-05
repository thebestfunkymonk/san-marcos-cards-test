import sys, warnings, itertools; sys.path.insert(0,'.'); sys.path.insert(0,'art')
warnings.simplefilter('ignore')
from deck import courtkit as K
import JC, _jc_body as B
import numpy as np
from shapely.geometry import Point, LineString
torso = B.region(*JC.TORSO)
jer = B.region(*JC.JERK).intersection(torso)
spec = JC.SLEEVE_R_SPEC
win = K.box(470, 380, 533, 480)
jl = jer.boundary.intersection(win)
res = []
grid = [[float(a) for a in s.split(',')] for s in sys.argv[1:6]]
for fy, bend, dist, bry, ww in itertools.product(*grid):
    mid = [(220.0, 438.0), (358.0, 444.0), (560.0, bry)]
    top = K.G.Curve(B.pts_of(B.spl([(x, y - 12.0) for x, y in mid])))
    bot = K.G.Curve(B.pts_of(B.spl([(x, y + 12.0) for x, y in mid])))
    tl = LineString(top.pts if hasattr(top,'pts') else B.pts_of(B.spl([(x, y - 12.0) for x, y in mid]))).intersection(win)
    bl_ = LineString(B.pts_of(B.spl([(x, y + 12.0) for x, y in mid]))).intersection(win)
    F=(548.0, fy)
    WR = np.array(K.fist_wrist(F, -90.0, bend=bend, dist=dist, **JC.FIST_KW))
    Bp = np.array(spec['base']); u = (WR - Bp)/np.hypot(*(WR-Bp)); n = np.array([u[1], -u[0]])
    wl, wr = WR + n*ww/2, WR - n*ww/2
    cl, cr = wl - u*spec['cuff'], wr - u*spec['cuff']
    corners = {'wl': wl, 'wr': wr, 'cl': cl, 'cr': cr}
    lines = {'btop': tl, 'bbot': bl_, 'jerk': jl}
    ds = {f"{c}-{l}": lines[l].distance(Point(*p)) for c, p in corners.items() for l in lines}
    # hand contour vs jerkin edge (outside the cuff/sleeve)
    sc = K.Scene(rank='J')
    sl, cf = K.sleeve(K.SleeveSpec(wrist=tuple(WR), folds=0, **{**spec, 'wrist_w': ww}))
    sc.part('sleeveR', sl); sc.part('cuffR', cf)
    h = K.fist(F, -90.0, wrist=tuple(WR), wrist_w=26.0, hand='L', **JC.FIST_KW).tucked(sc)
    hb = h.shape.boundary.difference(cf.shape.buffer(1.0)).difference(sl.shape.buffer(1.0))
    dj = hb.distance(jl); xj = hb.intersects(jl)
    dh_top = hb.distance(tl)
    ds['hand-jerk'] = 99.0 if xj else dj
    worst = min(ds.values())
    res.append((round(worst,1), fy, bend, dist, bry, ww, WR.round(1).tolist(), {k: round(v,1) for k, v in ds.items() if v < 6}))
res.sort(key=lambda r: -r[0])
for r in res[:20]: print(r)
