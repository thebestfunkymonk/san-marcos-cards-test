import sys
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/build/review/courts2-KH/work')
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/build/review/courts2-KH/work/r2')
from geomplot import plot
import scan as S, numpy as np
from shapely.geometry import Point, MultiPoint
from deck import courtkit as K
import art.KH as KH
side, bend, dist = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
kw = eval('dict(' + (sys.argv[5] if len(sys.argv) > 5 else '') + ')')
ft = kw.pop('fist_t', 0.0)
if ft:
    F0 = K.P(KH.FIST); T = K.P(KH.POLE_TOP); U = (T - F0) / np.hypot(*(T - F0)); KH.FIST = tuple(F0 + U * ft)
W, B, s, c, h = S.seat(side, bend, dist, **kw)
Wp, Bp, m = S.metrics(side, bend, dist, **kw)
F = m['F']
cF = S.corners(F)
box = (139, 360, 290, 511) if side == 'L' else (460, 390, 611, 511)
items = [(S.RS.boundary, 'black', 'none', 1.2), (S.SEAM, 'blue', 'none', 0.6),
         (s, 'green', 'green', 0.5), (c, 'darkgreen', 'teal', 0.5), (h, 'orange', 'yellow', 0.5),
         (S.pole.shape, 'brown', 'none', 0.4), (S.chal.shape, 'brown', 'none', 0.4), (S.WIN.boundary, 'grey', 'none', 0.5)]
items += [(Point(*p).buffer(0.8), 'red', 'red', 0.2) for p in cF]
plot(items, box, sys.argv[4], scale=5)
print({k: round(float(v), 1) for k, v in m.items() if k != 'F'})
