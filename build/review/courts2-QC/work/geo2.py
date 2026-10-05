import sys, os
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import QC
from deck import courtkit as K
spec = dict(QC.SCEPTRE)
for ky in (281, 272, 270, 268):
    spec['knop_y'] = ky
    sp = QC.S.rice_sceptre(QC.SCEPTRE_X, **spec)
    kn = K.R(K.rrect(541-13, ky-6, 541+13, ky+6, 5.5))
    for g in K._polys_of(sp.meta['head']):
        print(ky, [round(v,1) for v in g.bounds], 'd knop', round(g.distance(kn),2))
