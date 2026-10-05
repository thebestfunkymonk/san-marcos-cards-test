import sys, warnings; sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np
from shapely.geometry import LineString
from deck import courtkit as K
p0, p1 = np.array((352.,296.)), np.array((482.,545.))
u = (p1-p0)/np.hypot(*(p1-p0)); n = np.array([u[1],-u[0]])
W = float(sys.argv[1])
for cn in np.arange(-3.0, 0.01, 0.25):
    c = p0 + u*63.0 + n*cn
    sil = K.lion_clasp(tuple(c), 40.0).meta['silhouette']
    R = LineString([p0+n*W/2-u*300, p1+n*W/2+u*300]); L = LineString([p0-n*W/2-u*300, p1-n*W/2+u*300])
    print(round(cn,2), tuple(np.round(c,2)), 'R %.2f L %.2f' % (sil.distance(R) - K.FINE/2 - K.MEDIUM/2, sil.distance(L) - K.FINE/2 - K.MEDIUM/2))
