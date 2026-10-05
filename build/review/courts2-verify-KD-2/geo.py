import sys, warnings
warnings.simplefilter("ignore")
sys.path.insert(0, ".")
import shapely
from shapely.geometry import Point, box
from deck import courtkit as K
from art import KD
sc = KD.figure()
it = {i.name: i for i in sc.items}
print([i.name for i in sc.items])
sl, cf = it["sleeveL"].occ, it["cuffL"].occ
z = box(290, 410, 335, 450)
out = sl.difference(cf).intersection(z)
print("sleeveL outside cuffL in zone: area", round(out.area,2), out.bounds)
# distance between sleeve boundary and cuff boundary along cuff's upper-left edge
import numpy as np
cb = cf.exterior
sbd = sl.exterior
for t in np.linspace(0, 1, 13):
    p = np.array((325,420.5))*(1-t)+np.array((300,442))*t
    P = Point(*p)
    print(tuple(np.round(p,1)), "d cuff edge", round(cb.distance(P),2), "d sleeve edge", round(sbd.distance(P),2), "in sleeve", sl.contains(P))
