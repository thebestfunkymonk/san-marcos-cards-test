"""pieces.py <module> x0 y0 x1 y1 — pre-heal connected pieces per mark group inside the box (small ones)."""
import sys, warnings
sys.path.insert(0, '.')
warnings.simplefilter('ignore')
import importlib.util
import shapely
from shapely.geometry import box
from deck import courtkit as K
from inkkit import geom as G
spec = importlib.util.spec_from_file_location('kdp', sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
bx = box(*map(float, sys.argv[2:6]))
sc = m.figure()
res = sc.compose(heal_gaps=False)
marks = list(res.marks)
outl = {i: K.R(G.from_skia(mk.skia())) for i, mk in enumerate(marks) if mk.d}
for grp in K._groups(marks):
    u = shapely.union_all([outl[i] for i in grp if i in outl])
    for pg in K._polys_of(u):
        if pg.intersects(bx) and pg.area < 400:
            roles = sorted({marks[i].role for i in grp if outl[i].intersects(pg)})
            c = pg.representative_point()
            print(f"{marks[grp[0]].kind:6s} {marks[grp[0]].layer:5s} area={pg.area:7.1f} at=({c.x:.1f},{c.y:.1f}) bounds={tuple(round(v,1) for v in pg.bounds)} roles={roles}")
