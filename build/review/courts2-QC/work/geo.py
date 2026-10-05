import sys, os
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import QC
from deck import courtkit as K
from shapely.geometry import Point, box
sc, fc = QC.figure()
it = {i.name: i for i in sc.items}
sp = QC.S.rice_sceptre(QC.SCEPTRE_X, **QC.SCEPTRE)
hair = it['hairR'].occ
head = sp.meta['head']
print('head-hair dist', head.distance(hair.boundary), 'intersects', head.intersects(hair))
for g in K._polys_of(head):
    if g.bounds[0] < 500:
        print('piece', [round(v,1) for v in g.bounds], 'dist to hair edge', round(g.distance(hair.exterior),2), 'inter', g.intersects(hair))
cl = it['cloak'].occ
print('cloak bounds', cl.bounds)
# cloak top edge y at x = 520..560
import numpy as np
for x in (520, 528, 533, 541, 549, 554, 560):
    ln = box(x-0.01, 200, x+0.01, 320).intersection(cl)
    print(x, ln.bounds[1] if not ln.is_empty else None)
# right sleeve/cuff/culm geometry
for nm in ('sleeveR','cuffR','handR','culm','gown','sleeveL','cuffL','handL'):
    print(nm, [round(v,1) for v in it[nm].occ.bounds])
print('WL', QC.K.fist_wrist(QC.FIST_L, QC.FAN_AXIS, bend=52.0, dist=0.9, shaft_w=10.0, back=-1, h=32.0))
print('WR', QC.K.fist_wrist(QC.FIST_R, -90.0, bend=45.0, shaft_w=19.0, back=-1, h=34.0))
g = K.fist_geom(QC.FIST_L, QC.FAN_AXIS, shaft_w=10.0, back=-1, h=32.0); print('geomL', {k:(np.round(v,1) if hasattr(v,'__len__') else round(v,2)) for k,v in g.items()})
g = K.fist_geom(QC.FIST_R, -90, shaft_w=19.0, back=-1, h=34.0); print('geomR', {k:(np.round(v,1) if hasattr(v,'__len__') else round(v,2)) for k,v in g.items()})
print('face', fc.anchors.get('chin'), {k: v for k, v in fc.anchors.items() if k in ('chin','top','eye_y','axis')})
print(fc.head.bounds if hasattr(fc.head,'bounds') else K.R(fc.head).bounds)
