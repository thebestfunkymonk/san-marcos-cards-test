import sys, os, warnings
ROOT = '/home/luke/Projects/design/san-marcos-deck'
sys.path.insert(0, ROOT); os.chdir(ROOT); warnings.simplefilter('ignore')
import numpy as np, shapely
from shapely.geometry import LineString, Point
from deck import courtkit as K
import art.KH as KH, art._kh_parts as KP
crown, posts, pearls = KP.post_crown2()
band = crown.shape
occ = {'pearl%d' % i: p for i, p in enumerate(posts.meta and pearls.meta['pearls'])}
for i, p in enumerate(posts.meta['posts']):
    occ['post%d' % i] = p.difference(pearls.shape)
occ['band'] = band
def tangent_angle(geom, pt, dirv):
    b = geom.boundary
    d = b.project(pt)
    a = np.asarray(b.interpolate(max(d - 0.8, 0)).coords[0]); c = np.asarray(b.interpolate(d + 0.8).coords[0])
    t = c - a; t /= np.hypot(*t) + 1e-9
    return float(np.degrees(np.arccos(abs(t @ dirv))))
def evaluate(tx, fist=KH.FIST, w=18.0, verbose=False):
    p0, p1 = K.P(fist), K.P((tx, 55.0))
    u = (p1 - p0) / np.hypot(*(p1 - p0)); n = np.array([u[1], -u[0]])
    worst = 90.0; notes = []
    for sgn, nm in ((-1, 'L'), (1, 'R')):
        off = n * sgn * w / 2
        e = LineString([tuple(p0 + off - u * 50), tuple(p1 + off + u * 60)])
        front = shapely.union_all(list(occ.values()))
        vis = e.difference(front)
        for g in K._lines_of(vis):
            if g.length < 0.5: continue
            for q in (g.coords[0], g.coords[-1]):
                pt = Point(q)
                if not (100 < q[1] < 200): continue
                # which occluder
                dists = {k: v.boundary.distance(pt) for k, v in occ.items()}
                k = min(dists, key=dists.get)
                if dists[k] > 0.5: continue
                ang = tangent_angle(occ[k], pt, u)
                notes.append((nm, k, round(q[0], 1), round(q[1], 1), round(ang, 1), round(g.length, 1)))
                worst = min(worst, ang)
        # near misses: visible edge within 1..6 px of an occluder boundary it does not touch there
        for k, v in occ.items():
            dd = vis.distance(v)
            if 0.3 < dd < 6.0:
                notes.append((nm, k, 'near-miss', round(dd, 2)))
                worst = min(worst, 0.0)
    return worst, notes
if __name__ == '__main__':
    for tx in [float(x) for x in sys.argv[1].split(',')]:
        w, notes = evaluate(tx)
        print(tx, round(w, 1), notes)

def summary(tx, **kw):
    w, notes = evaluate(tx, **kw)
    ends = [n for n in notes if n[2] != 'near-miss']
    nm = [n for n in notes if n[2] == 'near-miss']
    angs = [n[4] for n in ends]
    lens = [n[5] for n in ends]
    return min(angs, default=90), min(lens, default=99), nm, ends
