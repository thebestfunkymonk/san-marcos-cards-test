import sys, warnings, itertools
sys.path.insert(0, '.'); warnings.simplefilter('ignore')
import numpy as np
from shapely.geometry import LineString, Point
from deck import courtkit as K
import art.KH as KH
from art import _kh_parts as KP

robe_m, rip, robe_inner = KP.robe(KH.ROBE, border=30.0, pitch=(96.0, 36.0), origin=(K.AX, 312.0))
RS = robe_m.shape.boundary
SEAM = robe_inner.boundary

def pts_of(x):
    if x.is_empty: return []
    if x.geom_type == 'Point': return [x]
    return [g for g in getattr(x, 'geoms', []) if g.geom_type == 'Point']

def arm(side, bend, dist, width, wrist_w, cuff=20.0, reach=110.0):
    if side == 'L':
        at, ax, hk = KH.GRIP_L, -90.0, KH.HAND_L
    else:
        at, ax, hk = KH.FIST, KH.POLE_DEG, KH.HAND_R
    W, B = KH._arm(at, ax, hk, bend, dist, reach)
    B, Wp = K.P(B), K.P(W)
    u = (Wp - B) / np.hypot(*(Wp - B)); n = np.array([u[1], -u[0]])
    bl, br = B + n*width/2, B - n*width/2
    wl, wr = Wp + n*wrist_w/2, Wp - n*wrist_w/2
    cl, cr = wl - u*cuff, wr - u*cuff
    corners = dict(wl=wl, wr=wr, cl=cl, cr=cr)
    res = {}
    for en, a, b in (('top+n', bl, wl), ('bot-n', br, wr)):
        ls = LineString([tuple(a), tuple(b)])
        for nm, bnd in (('contour', RS), ('seam', SEAM)):
            for p in pts_of(ls.intersection(bnd)):
                d = min(np.hypot(p.x-c[0], p.y-c[1]) for c in corners.values())
                res.setdefault(nm, []).append((en, round(p.x,1), round(p.y,1), round(float(d),1)))
    # cuff edges vs seam/contour
    cuff_poly = [wl, wr, cr, cl]
    for i in range(4):
        e = LineString([tuple(cuff_poly[i]), tuple(cuff_poly[(i+1)%4])])
        for nm, bnd in (('contour', RS), ('seam', SEAM)):
            for p in pts_of(e.intersection(bnd)):
                d = min(np.hypot(p.x-c[0], p.y-c[1]) for c in corners.values())
                res.setdefault(nm+'@cuff', []).append((i, round(p.x,1), round(p.y,1), round(float(d),1)))
    return W, B, corners, res

if __name__ == '__main__':
    for side, bend, dist, width, ww in (('L', 45, 1.10, 84, 40), ('R', 55, 1.02, 82, 38)):
        W, B, c, r = arm(side, bend, dist, width, ww)
        print(side, np.round(W,1), {k: np.round(v,1).tolist() for k,v in c.items()})
        for k, v in r.items(): print('  ', k, v)
