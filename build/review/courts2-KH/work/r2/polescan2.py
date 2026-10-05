import sys, os, warnings
ROOT = '/home/luke/Projects/design/san-marcos-deck'
sys.path.insert(0, ROOT); os.chdir(ROOT); warnings.simplefilter('ignore')
import numpy as np, shapely
from shapely.geometry import LineString, Point
from deck import courtkit as K
import art.KH as KH, art._kh_parts as KP
crown, posts, pearls = KP.post_crown2()
band = crown.shape
PR = pearls.meta['pearls']; PO = [p.difference(pearls.shape) for p in posts.meta['posts']]
occ_e = shapely.union_all([p.buffer(1.6) for p in PR] + [p.buffer(1.6) for p in PO])
def angle_at(geom, pt, u):
    b = geom.boundary; d = b.project(pt)
    a = np.asarray(b.interpolate(max(d - 0.8, 0)).coords[0]); c = np.asarray(b.interpolate(d + 0.8).coords[0])
    t = c - a; t /= np.hypot(*t) + 1e-9
    return float(np.degrees(np.arccos(min(1, abs(t @ u)))))
def edges(tx, w, fist=KH.FIST):
    p0, p1 = K.P(fist), K.P((tx, 55.0))
    u = (p1 - p0) / np.hypot(*(p1 - p0)); n = np.array([u[1], -u[0]])
    out = []
    for sgn in (-1, 1):
        off = n * sgn * w / 2
        e = LineString([tuple(p0 + off - u * 50), tuple(p1 + off + u * 60)])
        # contour: visible outside the (buffered) posts/pearls, and above the band (the band hides it)
        vis = e.difference(occ_e).difference(band)
        pieces = [g for g in K._lines_of(vis) if g.bounds[1] < 150 and g.bounds[3] > 95]
        info = []
        for g in pieces:
            ends = []
            for q in (g.coords[0], g.coords[-1]):
                pt = Point(q)
                if q[1] < 60: continue
                # which occluder ends it
                cand = [('pearl%d' % i, p) for i, p in enumerate(PR)] + [('post%d' % i, p) for i, p in enumerate(PO)] + [('band', band)]
                k, geo = min(cand, key=lambda c: c[1].distance(pt))
                ends.append((k, round(angle_at(geo, Point(geo.boundary.interpolate(geo.boundary.project(pt))), u), 1)))
            info.append((round(g.length, 1), ends))
        # near-parallel close runs: the visible edge within 1.6..6 px of a post stem / pearl it does not end at
        out.append(info)
    return out
if __name__ == '__main__':
    import itertools
    txs = [float(x) for x in sys.argv[1].split(',')] if ',' in sys.argv[1] else list(np.arange(*[float(v) for v in sys.argv[1].split(':')]))
    ws = [float(x) for x in sys.argv[2].split(',')]
    for w in ws:
        for tx in txs:
            print(round(tx, 2), w, edges(tx, w))
