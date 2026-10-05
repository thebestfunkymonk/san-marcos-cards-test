import sys
sys.path.insert(0, "art")
exec(open("build/review/courts2-QC/r3/leftsearch2.py").read().split("why = collections.Counter()")[0])
corner = K.Point(280.8, 440.8)
tzr = K.R(kw['tip_zone'])
for L in (125.0, 120.0, 115.0):
  W = max(L / kw['ratio'], kw['min_w'])
  for bd in (kw['bend'], (-kw['bend'][0], -kw['bend'][1]), (6.0, -6.0), (0.0, 0.0)):
    for s_across in (4, 5, 6, 7, 8):
        for s_along in (0, 2, 4, 6, 8, 10):
            base = np.array([250.0, 416.0]) + v * s_across + u * s_along
            pg = GW.leaf_poly(base, H, L, W, bd)
            sp = GW._spikes(base, H, L, bd)
            dz = [round(tzr.boundary.distance(Point(*q)) * (1 if tzr.contains(Point(*q)) else -1), 1) for q in sp]
            vis = pg.difference(soft_r); pcs = K._polys_of(vis)
            fr = sorted(round(q.area / pg.area, 2) for q in pcs)
            sl = GW._grazes(pg, vis, soft_r, *kw['sliver'])
            tipc = [round(soft_r.distance(Point(*q)), 1) for q in (base, base + u * L)]
            if min(dz) > -1.5 and min(fr) >= 0.2 and not sl:
                print(L, bd, s_across, s_along, "tz", dz, "frac", fr, "tipclear", tipc, f"corner {pg.boundary.distance(corner):.1f}")
