import sys, importlib
sys.path.insert(0, '.')
import shapely
from shapely.geometry import Point
from art import QH, _qh_attr as A
importlib.reload(A); importlib.reload(QH)
sc = QH.figure()
occ = shapely.union_all([it.occ for it in sc.items if it.occ is not None and it.name != "bubbles"])
bub = [it for it in sc.items if it.name == "bubbles"][0]
f = A.bubble_ribbon(QH.AIR, QH.AIR_SIZES, growth=QH.AIR_GROWTH)
print("path len", round(shapely.LineString(f.meta['path']).length,1), "gaps", [round(g,1) for g in f.meta['gaps']])
for (c, Do), d in zip(f.meta["discs"], QH.AIR_SIZES):
    dist = occ.distance(Point(*c)) - Do/2 - 3.125
    print(f"{str(d):16s} outer {Do:5.2f} at ({c[0]:6.1f},{c[1]:6.1f})  paper to contour {dist:5.1f}  to gold rule top {c[1]-Do/2-51-1.05:5.1f}")
