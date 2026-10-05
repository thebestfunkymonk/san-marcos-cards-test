import sys, importlib.util
sys.path.insert(0, '.'); sys.path.insert(0, 'art')
from deck import courtkit as K
from inkkit import geom as G
import shapely
pid = sys.argv[1]
spec = importlib.util.spec_from_file_location(pid, f'art/{pid}.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
res = sc.compose()
bbox = [float(v) for v in sys.argv[2].split(',')] if len(sys.argv) > 2 else None
box = K.box(*bbox) if bbox else None
for mk in res.marks:
    if mk.kind == 'fill' and mk.d:
        g = G.to_shape(mk.d, tol=0.1)
        if box is not None and g.intersects(box):
            print(mk.layer, mk.kind, mk.role, round(g.intersection(box).area,1))
    elif box is not None and mk.d:
        try:
            g = G.to_shape(G.outline(mk.d, mk.width), tol=0.1)
        except Exception as e:
            continue
        if g.intersects(box): print(mk.layer, mk.kind, mk.role, mk.width, round(g.intersection(box).area,1))
print('heal log', len(sc.heal_log))
for e in sc.heal_log[:60]: print('  ', e)
