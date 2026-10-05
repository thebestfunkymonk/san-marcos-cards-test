"""Geometric scan of the arm seating: bend/dist per side -> junction clearances."""
import sys, warnings, itertools
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck'); warnings.simplefilter('ignore')
import numpy as np, shapely
from shapely.geometry import LineString, Point, Polygon
from deck import courtkit as K
import art.KH as KH
from art import _kh_parts as KP, _kh_hands as KHN

robe_m, rip, robe_inner = KP.robe(KH.ROBE, border=30.0, pitch=(96.0, 36.0), origin=(K.AX, 312.0))
RS = robe_m.shape
SEAM = robe_inner.boundary
chal = KP.chalice(KH.CHAL_X, KH.CHAL_RIM, rim_hw=29.0, bowl_h=44.0, stem_len=KH.CHAL_STEM + KH.CHAL_FOOT_DROP,
                  foot_hw=KH.CHAL_FOOT, tip_r=KH.CHAL_TIP_R, engrave_gap=KH.CHAL_ENGRAVE_GAP)
lo, hi = KH._pole_line()
pole = KP.pole(lo, hi, round_low=False, **KH.POLE_KW)
WIN = K.box(139, 55, 611, 511)

def pts(x):
    if x.is_empty: return []
    if x.geom_type == 'Point': return [x]
    out = []
    for g in getattr(x, 'geoms', []):
        if g.geom_type == 'Point': out.append(g)
        elif g.geom_type == 'LineString': out += [Point(g.coords[0]), Point(g.coords[-1])]
    return out

def corners(poly, ang=35.0):
    c = np.asarray(poly.exterior.coords)[:-1]
    out = []
    n = len(c)
    for i in range(n):
        a, b, d = c[i-1], c[i], c[(i+1) % n]
        v1, v2 = b - a, d - b
        if np.hypot(*v1) < 1e-6 or np.hypot(*v2) < 1e-6: continue
        t = np.degrees(np.arccos(np.clip(v1 @ v2 / np.hypot(*v1) / np.hypot(*v2), -1, 1)))
        if t > ang: out.append(b)
    return np.asarray(out)

def seat(side, bend, dist, width=None, wrist_w=None, cuff=20.0, reach=110.0, wrist_hw=None):
    if side == 'L':
        at, ax, hk, SL, ww = KH.GRIP_L, -90.0, KH.HAND_L, KH.SLEEVE_L, 26.0
    else:
        at, ax, hk, SL, ww = KH.FIST, KH.POLE_DEG, KH.HAND_R, KH.SLEEVE_R, 27.0
    W, B = KH._arm(at, ax, hk, bend, dist, reach)
    sl = dict(SL); sl['base'] = B; sl['cuff'] = cuff
    if width: sl['width'] = width
    if wrist_w: sl['wrist_w'] = wrist_w
    s, c = K.sleeve(K.SleeveSpec(wrist=W, color=K.JADE, cuff_color=K.JADE, **sl))
    h = K.fist(at, ax, wrist=W, wrist_w=wrist_hw or ww, **hk)
    h = KHN.straight_heel(h, at, ax, **hk)
    hand = h.hand.shape.union(h.thumb.shape) if h.thumb is not None else h.hand.shape
    return W, B, s.shape, c.shape, hand

def metrics(side, bend, dist, **kw):
    W, B, s, c, hnd = seat(side, bend, dist, **kw)
    F = shapely.union_all([s, c, hnd]).intersection(WIN)
    m = {}
    # 1) robe contour meets the sleeve: concave corner(s) outside the cuff/hand
    X = [p for p in pts(RS.boundary.intersection(s.boundary)) if WIN.buffer(-1).contains(p)]
    X = [p for p in X if c.buffer(-0.5).disjoint(p) and hnd.buffer(-0.5).disjoint(p)]
    m['cc_cuff'] = min([p.distance(c) for p in X], default=99)
    m['cc_frame'] = min([min(p.x - 139, 611 - p.x, 511 - p.y) for p in X], default=99)
    # robe contour crossing the cuff or hand directly
    m['contour_on_cuff'] = RS.boundary.intersection(c.buffer(-0.5)).length
    # 2) seam ends at F's boundary
    vis = SEAM.intersection(WIN).difference(F.buffer(-0.01))
    ends = []
    for g in K._lines_of(vis):
        if g.length < 30: continue      # drop_stubs removes these
        for q in (g.coords[0], g.coords[-1]):
            p = Point(q)
            if p.distance(F.boundary) < 0.5: ends.append(p)
    cF = corners(F) if F.geom_type == 'Polygon' else np.zeros((0, 2))
    cc = corners(c)
    m['seam_corner'] = min([min(float(np.min(np.hypot(*(cF - [p.x, p.y]).T))) if len(cF) else 99,
                                float(np.min(np.hypot(*(cc - [p.x, p.y]).T)))) for p in ends], default=99)
    # 3) clearance to the attribute
    att = chal.shape.intersection(K.box(0, 400, 750, 750)) if side == 'L' else pole.shape
    m['att_gap'] = min(att.distance(s), att.distance(c))
    m['F'] = F
    return W, B, m

if __name__ == '__main__':
    side = sys.argv[1]
    bends = [float(x) for x in sys.argv[2].split(',')]
    dists = [float(x) for x in sys.argv[3].split(',')]
    for b in bends:
        for d in dists:
            W, B, m = metrics(side, b, d)
            print(side, b, d, 'W', np.round(W, 1), 'B', np.round(B, 1),
                  {k: round(float(v), 1) for k, v in m.items() if k != 'F'})
