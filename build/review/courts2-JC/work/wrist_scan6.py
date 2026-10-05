import sys, warnings, itertools, math; sys.path.insert(0,'.'); sys.path.insert(0,'art')
warnings.simplefilter('ignore')
from deck import courtkit as K
import JC, _jc_body as B
import numpy as np
from shapely.geometry import Point, LineString
torso = B.region(*JC.TORSO)
jer = B.region(*JC.JERK).intersection(torso)
spec = JC.SLEEVE_R_SPEC
win = K.box(470, 380, 531, 480)
jl = jer.boundary.intersection(win)
bl = B.reed_belt(torso, y=440.0, h=24.0, sag=4.0, x0=220.0, x1=560.0, front=358.0, rise=JC.BELT_RISE)
bpts = np.asarray(bl.shape.exterior.coords)
tl = LineString([p for p in bpts if p[1] < 440 and 470 < p[0] < 540])
tl = LineString(sorted([tuple(p) for p in bpts if 470 < p[0] < 540 and p[1] < 438], key=lambda q: q[0]))
bb = LineString(sorted([tuple(p) for p in bpts if 470 < p[0] < 540 and p[1] > 440], key=lambda q: q[0]))
def angle_at(a, b, p):
    # tangent angle of lines a and b near p
    def tan(l):
        s = l.project(Point(*p)); p0 = l.interpolate(max(s-2,0)); p1 = l.interpolate(min(s+2,l.length))
        return math.atan2(p1.y-p0.y, p1.x-p0.x)
    d = abs(math.degrees(tan(a) - tan(b))) % 180
    return min(d, 180 - d)
res = []
grid = [[float(a) for a in s.split(",")] for s in sys.argv[1:6]]
for fy, bend, dist, ww, bx in itertools.product(*grid):
    spec = {**JC.SLEEVE_R_SPEC, "base": (bx, 552.0)}
    F=(548.0, fy)
    WR = np.array(K.fist_wrist(F, -90.0, bend=bend, dist=dist, **JC.FIST_KW))
    Bp = np.array(spec['base']); u = (WR - Bp)/np.hypot(*(WR-Bp)); n = np.array([u[1], -u[0]])
    wl, wr = WR + n*ww/2, WR - n*ww/2
    cl, cr = wl - u*spec['cuff'], wr - u*spec['cuff']
    corners = {'wl': wl, 'cl': cl}
    lines = {'btop': tl, 'bbot': bb, 'jerk': jl}
    ds = {f"{c}-{l}": lines[l].distance(Point(*p)) for c, p in corners.items() for l in lines}
    sc = K.Scene(rank='J')
    sl, cf = K.sleeve(K.SleeveSpec(wrist=tuple(WR), folds=0, **{**spec, 'wrist_w': ww}))
    sc.part('sleeveR', sl); sc.part('cuffR', cf)
    h = K.fist(F, -90.0, wrist=tuple(WR), wrist_w=26.0, hand='L', **JC.FIST_KW).tucked(sc)
    hb = h.shape.boundary.difference(cf.shape.buffer(1.0)).difference(sl.shape.buffer(1.0)).intersection(win)
    for nm, l in (('jerk', jl),):
        if hb.intersects(l):
            ip = hb.intersection(l)
            pts = [ip] if ip.geom_type == 'Point' else list(getattr(ip, 'geoms', []))
            angs = [angle_at(max(K._lines_of(hb), key=lambda g: -g.distance(q)), l, (q.x, q.y)) for q in pts if q.geom_type == 'Point']
            ds[f'hand-{nm}'] = 99.0 if (angs and min(angs) > 25) else (min(angs) / 10 if angs else 0.0)
        else:
            ds[f'hand-{nm}'] = hb.distance(l)
    worst = min(ds.values())
    res.append((round(worst,1), fy, bend, dist, ww, bx, WR.round(1).tolist(), {k: round(v,1) for k, v in ds.items() if v < 6}))
res.sort(key=lambda r: -r[0])
for r in res[:14]: print(r)
