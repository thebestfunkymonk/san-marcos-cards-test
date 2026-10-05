import sys; sys.path.insert(0,'.')
import numpy as np
from shapely.geometry import Point
from art import _kc_robe as RB, KC
from deck import courtkit as K
rkw = dict(KC.ROBE)
rb0 = RB.robe(**{**rkw, "fluting": False})
zone = rb0.meta['inner'].buffer(-0.05)
seam = zone.boundary
def rx(X,y): return 375 - X*(y+400)/911
for y in range(330, 420, 6):
    p = Point(rx(191,y), y)
    print(y, round(rx(191,y),1), 'seam dist %.2f' % seam.distance(p), 'in zone', zone.contains(p))
