"""healdiff.py [overrides...] — where heal removed ink/fill: components of (pre-heal − post-heal) per layer, role."""
import sys, os, warnings, json
ROOT = '/home/luke/Projects/design/san-marcos-deck'
sys.path.insert(0, ROOT); os.chdir(ROOT); warnings.simplefilter('ignore')
import numpy as np, shapely
from deck import courtkit as K
from deck.motifs import core as C
import art.KH as KH, art._kh_parts as KP, art._kh_hands as KHN
for m in sys.argv[1:]:
    exec(m, {'KH': KH, 'K': K, 'np': np, 'KP': KP, 'KHN': KHN})
sc = KH.figure()
pre = sc.compose(heal_gaps=False)
sc2 = KH.figure()
post = sc2.compose(heal_gaps=True)
def by(f):
    out = {}
    for m in f.marks:
        key = (m.layer, (m.role or m.kind).split('@')[0])
        try:
            g = K.R(C.Frag([m]).outline())
        except Exception:
            continue
        out.setdefault(key, []).append(g)
    return {k: shapely.union_all(v) for k, v in out.items()}
A, B = by(pre), by(post)
res = []
for k, g in A.items():
    d = g.difference(B.get(k, shapely.Polygon()).buffer(0.05))
    for p in K._polys_of(d):
        if p.area > float(os.environ.get("HD_MIN", 1.5)):
            c = p.representative_point()
            if 139 <= c.x <= 611 and 55 <= c.y <= 511:
                res.append((round(p.area, 1), k, (round(c.x, 1), round(c.y, 1))))
res.sort(key=lambda r: (r[1], r[2]))
for r in res:
    print(r)
