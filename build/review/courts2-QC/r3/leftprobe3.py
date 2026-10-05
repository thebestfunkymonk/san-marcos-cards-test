import sys
sys.path.insert(0, "art")
exec(open("build/review/courts2-QC/r3/leftsearch2.py").read().split("why = collections.Counter()")[0])
it = {i.name: i for i in sc.items}
slL = it['sleeveL'].occ; cfL = it['cuffL'].occ
arm = slL.union(cfL)
tzr = K.R(kw['tip_zone'])
corner_pts = [Point(280.8, 440.8)]
res = []
for L in np.arange(70.0, 100.0, 2.5):
    W = max(L / 9.0, 12.6)
    for bd in ((6.0, -6.0), (12.0, -12.0), (0.0, 0.0)):
        for s_across in np.arange(-4, 9, 1.0):
            for s_along in np.arange(-8, 9, 2.0):
                base = np.array([250.0, 416.0]) + v * s_across + u * s_along
                pg = GW.leaf_poly(base, H, L, W, bd)
                sp = GW._spikes(base, H, L, bd)
                if not tzr.contains(Point(*sp[0])): continue
                d_low = slL.exterior.distance(Point(*sp[1])) if slL.contains(Point(*sp[1])) else -1
                if d_low < 8: continue
                vis = pg.difference(soft_r); pcs = K._polys_of(vis)
                if len(pcs) != 1: continue
                if GW._grazes(pg, vis, soft_r, *kw['sliver']): continue
                # where the leaf's outline crosses the arm: distance of those crossings to the cuff corner
                cross = pg.boundary.intersection(arm.boundary)
                cd = min(Point(280.8, 440.8).distance(pg.boundary), 99)
                tipclear = soft_r.distance(Point(*sp[0]))
                res.append((round(vis.area / pg.area, 2), L, bd, s_across, s_along, round(d_low, 1), round(cd, 1), round(tipclear, 1)))
res.sort(key=lambda r: (-r[0]))
for r in res[:40]: print(r)
print(len(res))
