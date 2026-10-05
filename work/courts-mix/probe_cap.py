import sys; sys.path.insert(0,'.'); sys.path.insert(0,'art')
import JC, _jc_parts as J, _jc_face as F
from deck import courtkit as K
from inkkit import geom as G
fc = F.face_jc(JC.HEAD, contour=JC.FACE_LOWER)
p = J.cap(fc, tip=(292.0, 171.0), top=(393.0, 106.0), flap_tip=(473.0, 130.0), hatband=10.5)
hb = p.meta['hatband']
print('hb bounds', hb.bounds, hb.area, hb.geom_type)
for mk in p.fills.marks:
    g = G.to_shape(mk.d, tol=0.05)
    print(mk.layer, g.geom_type, g.area, [len(pg.interiors) for pg in getattr(g,'geoms',[g])])
    if mk.layer=='jade':
        for pg in getattr(g,'geoms',[g]):
            for r in pg.interiors:
                from shapely.geometry import Polygon
                hole = Polygon(r)
                print(' hole', hole.bounds, hole.area, 'dist to ext', hole.exterior.distance(pg.exterior))
