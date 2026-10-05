import sys; sys.path.insert(0,'.')
import warnings; warnings.simplefilter('ignore')
from art import _kd_body as B
from deck import courtkit as K
from inkkit import geom as G
import numpy as np, shapely
def shp(f, roles):
    return shapely.union_all([K.R(G.from_skia(m.skia())) for m in f.marks if m.d and m.role.split('@')[0] in roles])
U=dict(r0=8.4, q=6.0, flat=2.0, leaf=(12.6,5.0))
for cw in [dict(width=36.0, flare=46.0, depth=36.0), dict(width=36.0, flare=44.0, depth=34.0), dict(width=36.0, flare=46.0, depth=34.0), dict(width=38.0, flare=46.0, depth=36.0)]:
  g = B.gauntlet((400.,400.), (1.0,-1.0), **cw)
  loc=g.meta['local']
  for gap in (3.0, 4.2):
    keep=loc.buffer(-(K.MEDIUM/2+gap+K.FINE/2+0.3))
    best=[]
    for x_first in np.arange(3.0,9.1,0.5):
      for yc in np.arange(-3.0,5.1,0.5):
        f=B.scroll_unit(x_first, yc, free=True, **U)
        vol=shp(f,("stem","volute","terminal","leaf"))
        best.append((round(vol.difference(keep).area,2), x_first, yc))
    best.sort(); print(cw, gap, best[:3])
