import sys; sys.path.insert(0,'.')
import numpy as np
from deck import courtkit as K
from art import KC, _kc_hands as H
WR = tuple(K.fist_wrist(KC.FIST, -90.0, **KC.FIST_WRIST, **KC.FIST_KW))
print('WR', WR)
g = K.fist_geom(KC.FIST, -90.0, **KC.FIST_KW)
print({k:(v if not hasattr(v,'shape') else np.round(v,2)) for k,v in g.items()})
fist = K.fist(KC.FIST, -90.0, wrist=WR, hand="L", **KC.FIST_HAND, **KC.FIST_KW)
xy = np.asarray(fist.hand.shape.exterior.coords)
sel = xy[(xy[:,1]>415)&(xy[:,1]<445)&(xy[:,0]>505)&(xy[:,0]<530)]
for p in sel: print(np.round(p,2))
