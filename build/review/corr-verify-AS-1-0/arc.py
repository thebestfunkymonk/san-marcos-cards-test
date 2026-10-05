import sys
sys.path.insert(0, '.')
from xml.etree import ElementTree as ET
from shapely import affinity
from inkkit import geom as G
NS = '{http://www.w3.org/2000/svg}'
def paths(p):
    r = ET.parse(p).getroot()
    return [el.get('d') for g in r.iter(NS+'g') if g.get('id') == 'gold' for el in g if el.tag == NS+'path']
b = paths('build/gallery/svg/AS.svg'); a = paths('cards/AS.svg')
for i, (dy, dx) in {len(b)-1: (75.6, 0.0), len(b)-3: (92.0, -0.22), len(b)-5: (92.0, -0.2), len(b)-6: (92.0, 0.03)}.items():
    sb = affinity.translate(G.to_shape(b[i], tol=0.01), dx, dy); sa = G.to_shape(a[i], tol=0.01)
    print(i, 'area before', round(sb.area, 2), 'after', round(sa.area, 2), 'symdiff', round(sb.symmetric_difference(sa).area, 3), 'hausdorff', round(sb.hausdorff_distance(sa), 3))
# all other gold paths: translate by 92 and compare
worst = 0
for i in range(len(b)-6):
    try:
        sb = affinity.translate(G.to_shape(b[i], tol=0.01), 0, 92); sa = G.to_shape(a[i], tol=0.01)
        if sb.area > 0.01:
            h = sb.hausdorff_distance(sa); worst = max(worst, h)
    except Exception as e:
        pass
print('fill-shape paths other: worst hausdorff after +92', round(worst, 3))
import numpy as np
for i in range(len(b)-6):
    pa = G.as_polys(a[i], 0.02); pb = G.as_polys(b[i], 0.02)
    A = np.vstack([np.asarray(p, float) for p, c in pa]); B = np.vstack([np.asarray(p, float) for p, c in pb]) + [0, 92]
    from shapely.geometry import MultiPoint
    h = MultiPoint(A).hausdorff_distance(MultiPoint(B))
    if h > 0.05: print('path', i, 'pointset hausdorff', round(h, 3), 'npts', len(A), len(B))
