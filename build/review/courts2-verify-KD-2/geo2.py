import sys, warnings
warnings.simplefilter("ignore")
sys.path.insert(0, ".")
import numpy as np, shapely
from shapely.geometry import Point, box, LineString
from deck import courtkit as K
from art import KD
sc = KD.figure()
it = {i.name: i for i in sc.items}
sl, cf = it["sleeveL"].occ, it["cuffL"].occ
hand = it["handL"].occ
# cuff exterior points in the zone
ext = np.asarray(cf.exterior.coords)
z = [p for p in ext if 295 <= p[0] <= 330 and 415 <= p[1] <= 447]
print("cuff edge pts in zone:", len(z), np.round(z[0],1), np.round(z[-1],1))
sliver = sl.difference(cf).difference(hand).intersection(box(295, 415, 330, 446))
print("sleeve sliver outside cuff (zone):", round(sliver.area,1), [tuple(np.round(g.bounds,1)) for g in getattr(sliver,'geoms',[sliver])])
# max width of sliver perpendicular: via inscribed radius sampling
for g in getattr(sliver,'geoms',[sliver]):
    if g.area < 0.5: continue
    b = g.bounds
    best = 0
    for x in np.arange(b[0], b[2], 0.25):
        for y in np.arange(b[1], b[3], 0.25):
            P = Point(x,y)
            if g.contains(P): best = max(best, g.exterior.distance(P))
    print("  piece area", round(g.area,1), "max width ~", round(2*best,2), "bounds", np.round(b,1))
