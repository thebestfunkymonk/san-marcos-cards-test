import sys, itertools, collections
sys.path.insert(0, "art")
import numpy as np
from shapely.geometry import Point
from shapely.prepared import prep
import QC
from deck import courtkit as K
import _qc_gown as GW
cap = {}
orig_pack = GW.leaf_pack
def spy(allowed, **kw):
    cap['allowed'] = allowed; cap['kw'] = kw
    return orig_pack(allowed, **kw)
GW.leaf_pack = spy
sc, fc = QC.figure()
allowed, kw = cap['allowed'], dict(cap['kw'])
left = K.box(150, 300, 356, 560)
al = allowed.intersection(left)
reg = al; pr = prep(reg)
soft_r = K.R(kw['soft']); tz = prep(K.R(kw['tip_zone']))
hide = K.R(kw['hide']); hide_p = prep(hide.buffer(-kw.get('hide_in', 7.0)))
soft_p = prep(soft_r.buffer(kw.get('tip_clear', 9.0)))
soft_s = prep(soft_r.buffer(3.0 + K.MEDIUM / 2 + 0.3))
ns = kw['no_show']
H = kw['heading']; u = GW._u(H); v = np.array([-u[1], u[0]])
why = collections.Counter(); ok = []
for L in (125.0, 110.0, 100.0, 90.0, 80.0):
    W = max(L / kw['ratio'], kw['min_w'])
    for bx in np.arange(200, 356, 2.0):
        for by in np.arange(300, 520, 2.0):
            base = np.array([bx, by])
            if not pr.contains(Point(*base)) or not pr.contains(Point(*(base + u * L))) or not pr.contains(Point(*(base + u * L / 2))):
                continue
            hid = [hide_p.contains(Point(*base)), hide_p.contains(Point(*(base + u * L)))]
            if sum(hid) > 1: why['bothhid'] += 1; continue
            if any(soft_p.contains(Point(*q)) and not h for q, h in zip((base, base + u * L), hid)): why['tipclear'] += 1; continue
            pg = GW.leaf_poly(base, H, L, W, kw['bend'])
            if not pr.contains(pg): why['notin'] += 1; continue
            sp = GW._spikes(base, H, L, kw['bend'])
            if not all(tz.contains(Point(*q)) for q in sp): why['tz'] += 1; continue
            if any(soft_s.contains(Point(*q)) and not hide_p.contains(Point(*q)) for q in sp): why['spike_soft'] += 1; continue
            if pg.intersects(soft_r):
                vis = pg.difference(soft_r); pcs = K._polys_of(vis)
                if vis.area < kw.get('min_visible', 0.5) * pg.area or len(pcs) > 2: why['vis'] += 1; continue
                if any(q.area < kw['min_piece'] for q in pcs): why['minpiece'] += 1; continue
                if any(q.area < kw['min_piece_frac'] * pg.area for q in pcs): why['frac'] += 1; continue
                cd = vis.distance(ns)
                if GW._grazes(pg, vis, soft_r, *kw['sliver']): why['sliver'] += 1; continue
            else:
                cd = 99
            ok.append((round(cd, 1), L, bx, by, [round(t) for t in pg.bounds]))
print(why)
ok.sort(key=lambda r: -r[0])
for r in ok[:30]: print(r)
print(len(ok))
print("---- corner relations (relaxed search, all lengths, no corner rule) ----")
corner = K.Point(280.8, 440.8)
arm = soft_r
for r in ok:
    pass
# relaxed: re-run allowing everything that passed, report distance of corner to leaf boundary
for (cd, L, bx, by, bb) in ok:
    W = max(L / kw['ratio'], kw['min_w'])
    pg = GW.leaf_poly(np.array([bx, by]), H, L, W, kw['bend'])
    print(L, bx, by, "corner→leaf edge", round(pg.boundary.distance(corner), 2), "inside" if pg.contains(corner) else "outside")
