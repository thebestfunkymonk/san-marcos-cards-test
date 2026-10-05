import sys; sys.path.insert(0,'.')
import numpy as np, json
from shapely.geometry import Point
from deck import courtkit as K
from art import KC
opts = json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
sc = KC.figure(opts)
res = sc.compose()
p = Point(560.3, 480)
for m in res.marks:
    if m.role.split('@')[0] == 'seam' and m.layer=='ink':
        for ln in K._stroke_lines(m.d):
            c = np.asarray(ln.coords)
            for e in (c[0], c[-1]):
                if Point(*e).distance(p) < 8: print('seam end', np.round(e,2))
st = [it for it in sc.items if it.name=='staff'][0]
halo = st.occ.buffer(st.halo + K.MEDIUM/2, quad_segs=12)
print('halo dist from end', [round(halo.distance(Point(*e)),2) for e in [(560.3,480)]])
for it in sc.items:
    if it.occ is not None and not it.occ.is_empty and it.occ.distance(p) < 6: print('item', it.name, round(it.occ.distance(p),2), it.halo)
e = Point(560.86, 480.57)
print('end->halo', round(halo.distance(e),2))
from shapely.ops import nearest_points
print('nearest halo pt', nearest_points(halo, e)[0])
# jade fill boundary near
for m in res.marks:
    if m.kind=='fill' and m.layer=='jade':
        g = K.G.to_shape(m.d, tol=0.05)
        print('jade dist', round(g.boundary.distance(e),2), nearest_points(g.boundary, e)[0])
