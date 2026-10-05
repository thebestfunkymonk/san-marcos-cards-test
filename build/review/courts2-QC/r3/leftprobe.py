import sys
sys.path.insert(0, "art")
exec(open("build/review/courts2-QC/r3/leftsearch2.py").read().split("why = collections.Counter()")[0])
corner = K.Point(280.8, 440.8)
L = 125.0; W = max(L / kw['ratio'], kw['min_w'])
for s_across in range(-10, 11, 2):
    for s_along in (-6, -3, 0, 3, 6):
        base = np.array([250.0, 416.0]) + v * s_across + u * s_along
        reasons = []
        hid = [hide_p.contains(Point(*base)), hide_p.contains(Point(*(base + u * L)))]
        for q, h in zip((base, base + u * L), hid):
            if soft_p.contains(Point(*q)) and not h:
                reasons.append(f"tipclear d={soft_r.distance(Point(*q)):.1f}")
        if not pr.contains(Point(*base)) or not pr.contains(Point(*(base + u * L))): reasons.append("tip-out")
        pg = GW.leaf_poly(base, H, L, W, kw['bend'])
        if not pr.contains(pg): reasons.append("notin")
        sp = GW._spikes(base, H, L, kw['bend'])
        if not all(tz.contains(Point(*q)) for q in sp): reasons.append("tz")
        vis = pg.difference(soft_r); pcs = K._polys_of(vis)
        if vis.area < 0.5 * pg.area or len(pcs) > 2: reasons.append(f"vis {vis.area/pg.area:.2f} n{len(pcs)}")
        if any(q.area < kw['min_piece_frac'] * pg.area for q in pcs): reasons.append("frac " + ",".join(f"{q.area/pg.area:.2f}" for q in pcs))
        if GW._grazes(pg, vis, soft_r, *kw['sliver']): reasons.append("sliver")
        print(s_across, s_along, [round(t) for t in base], f"corner {pg.boundary.distance(corner):.1f} {'in' if pg.contains(corner) else 'out'}", reasons)
