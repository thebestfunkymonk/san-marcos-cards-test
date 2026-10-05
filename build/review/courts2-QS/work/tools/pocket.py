import sys
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
from deck import courtkit as K
import art.QS as Q
sc = Q.figure()
for it in sc.items:
    if 'pocket' in it.name:
        print(it.name, [round(v,1) for v in it.halo_zone.bounds], round(it.halo_zone.area,1), it.halo_zone.geom_type)
