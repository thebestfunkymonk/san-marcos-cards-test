import sys, warnings; sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np
from shapely.geometry import LineString
from deck import courtkit as K
p0, p1 = np.array((352.,296.)), np.array((482.,545.))
u = (p1-p0)/np.hypot(*(p1-p0)); n = np.array([u[1],-u[0]])
for W in (48., 50., 52.):
  for size in (40.,):
    for dx in (0., -1., 1.):
        c = (381.0+dx, 352.0)
        cl = K.lion_clasp(c, size)
        sil = cl.meta['silhouette']
        R = LineString([p0+n*W/2-u*300, p1+n*W/2+u*300]); L = LineString([p0-n*W/2-u*300, p1-n*W/2+u*300])
        # clearance between clasp contour outer edge (sil + FINE/2) and sash edge stroke inner edge (MEDIUM/2)
        print(W, size, c, 'R %.2f L %.2f' % (sil.distance(R) - K.FINE/2 - K.MEDIUM/2, sil.distance(L) - K.FINE/2 - K.MEDIUM/2))
