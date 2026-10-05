import sys
sys.path.insert(0, "art")
exec(open("build/review/courts2-QC/r3/leftsearch2.py").read().split("why = collections.Counter()")[0])
it = {i.name: i for i in sc.items}
slL = it['sleeveL'].occ; cfL = it['cuffL'].occ
print("sleeveL bounds", slL.bounds)
tzr = K.R(kw['tip_zone'])
for L in (50.0, 55.0, 60.0, 65.0, 70.0, 80.0, 90.0, 100.0, 115.0):
    base = np.array([249.3, 424.5])
    sp = GW._spikes(base, H, L, (6.0, -6.0))
    q = Point(*sp[1])
    print(L, np.round(sp, 1), "in slL", slL.contains(q), round(slL.exterior.distance(q), 1), "tz0", tzr.contains(Point(*sp[0])))
