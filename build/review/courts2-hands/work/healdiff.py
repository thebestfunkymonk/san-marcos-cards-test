import warnings; warnings.simplefilter("ignore")
import sys; sys.path.insert(0,'.')
import shapely
from deck import build as B
from deck import courtkit as K
def scene(pid):
    m = B.load_art(pid)
    r = m.figure()
    sc = r[0] if isinstance(r, tuple) else r
    return m, sc
def comp(m, pid, sc, heal):
    if pid in ('QS','QD'):
        return m.compose_scene(sc) if heal else None
    return sc.compose(heal_gaps=heal)
ids = sys.argv[1:] or ['KS','QS','JS','KH','QH','JH','KC','QC','JC','KD','QD','JD']
for pid in ids:
    m, sc = scene(pid)
    hands = shapely.union_all([it.occ for it in sc.items if it.name.startswith('hand') and it.occ is not None])
    zone = hands.buffer(6)
    pre = sc.compose(heal_gaps=False)
    post = sc.compose(heal_gaps=True) if pid not in ('QS','QD','QC') else (m.compose_scene(sc) if pid != 'QC' else m.Q.compose(sc))
    def geo(f):
        gs=[]
        for mk in f.marks:
            if not mk.d: continue
            try: gs.append(K.R(K.G.from_skia(mk.skia())))
            except Exception: pass
        return shapely.union_all(gs).intersection(zone)
    a, b = geo(pre), geo(post)
    rem = a.difference(b.buffer(0.3))
    pcs = [g for g in K._polys_of(rem) if g.area > 2.0]
    print(pid, 'removed near hands:', [tuple(round(v) for v in g.bounds) + (round(g.area),) for g in pcs])
