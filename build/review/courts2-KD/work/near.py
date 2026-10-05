"""near.py <module> x y [r]  — marks (pre-heal) within r px of (x,y): role, layer, kind, distance."""
import sys, warnings
sys.path.insert(0, '.')
warnings.simplefilter('ignore')
import importlib.util
from shapely.geometry import Point
from deck import courtkit as K
from inkkit import geom as G
spec = importlib.util.spec_from_file_location('kdn', sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
x, y = float(sys.argv[2]), float(sys.argv[3]); r = float(sys.argv[4]) if len(sys.argv) > 4 else 5.0
sc = m.figure()
res = sc.compose(heal_gaps=False)
p = Point(x, y)
for mk in res.marks:
    if not mk.d: continue
    g = K.R(G.from_skia(mk.skia()))
    d = g.distance(p)
    if d <= r:
        print(f"{d:6.2f}  {mk.kind:6s} {mk.layer:5s} w={mk.w} role={mk.role}")
