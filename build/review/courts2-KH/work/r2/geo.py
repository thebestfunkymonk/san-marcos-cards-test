import sys, warnings
sys.path.insert(0, '.'); warnings.simplefilter('ignore')
import numpy as np
from shapely.geometry import LineString, Point
from deck import courtkit as K
import art.KH as KH
from art import _kh_parts as KP
for m in sys.argv[1:]:
    exec(m, {'KH': KH, 'K': K, 'np': np})
robe_m, rip, robe_inner = KP.robe(KH.ROBE, border=30.0, pitch=(96.0, 36.0), origin=(K.AX, 312.0))
rs = robe_m.shape
print('WL', np.round(KH.WL,1), 'baseL', np.round(KH.ARM_L_BASE,1), 'WR', np.round(KH.WR,1), 'baseR', np.round(KH.ARM_R_BASE,1))
for nm, W, SL in (('L', KH.WL, KH.SLEEVE_L), ('R', KH.WR, KH.SLEEVE_R)):
    s = K.SleeveSpec(wrist=W, **SL)
    B, Wp = K.P(s.base), K.P(W)
    u = (Wp - B) / np.hypot(*(Wp - B)); n = np.array([u[1], -u[0]])
    bl, br = B + n*s.width/2, B - n*s.width/2
    wl, wr = Wp + n*s.wrist_w/2, Wp - n*s.wrist_w/2
    cl, cr = wl - u*s.cuff, wr - u*s.cuff
    print(nm, 'u', np.round(u,3), 'angle', round(float(np.degrees(np.arctan2(-u[1], -u[0]))),1))
    for en, a, b, c in (('edge+n', bl, wl, cl), ('edge-n', br, wr, cr)):
        ls = LineString([tuple(a), tuple(b)])
        x = ls.intersection(rs.boundary)
        pts = [x] if x.geom_type == 'Point' else list(getattr(x, 'geoms', []))
        for p in pts:
            print('  ', en, 'crosses robe at', np.round([p.x, p.y],1), 'dist to cuff corner', round(float(np.hypot(p.x-c[0], p.y-c[1])),1), 'cuff corner', np.round(c,1), 'wrist corner', np.round(b,1))
