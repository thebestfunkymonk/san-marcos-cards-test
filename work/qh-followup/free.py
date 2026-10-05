import sys
sys.path.insert(0, '.')
import shapely
from shapely.geometry import box, LineString
from art import QH
sc = QH.figure()
occ = shapely.union_all([it.occ for it in sc.items if it.occ is not None and it.name not in ("hose","ferrule","bubbles")])
# for each y, free x-interval between head/hair and stem
for y in range(60, 320, 10):
    ln = LineString([(420, y), (611, y)])
    fr = ln.difference(occ)
    segs = [ (round(g.coords[0][0],1), round(g.coords[-1][0],1)) for g in getattr(fr,'geoms',[fr]) if not g.is_empty]
    print(y, segs)
print()
for x in range(470, 540, 5):
    ln = LineString([(x, 150), (x, 360)])
    inter = ln.intersection(occ)
    ys = [g.bounds[1] for g in getattr(inter,'geoms',[inter]) if not g.is_empty]
    print(x, [round(v,1) for v in sorted(ys)][:3])
