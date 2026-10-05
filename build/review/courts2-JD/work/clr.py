"""clr.py [module] : min stroke-edge gaps of each cuff's sprig (stem pieces minus their 8 px ends,
volute eye, terminal, leaves) to the cuff outline, the hand outline and the band rule."""
import sys, importlib.util
sys.path.insert(0, '.'); sys.path.insert(0, 'art')
path = sys.argv[1] if len(sys.argv) > 1 else 'art/JD.py'
spec = importlib.util.spec_from_file_location('jdm', path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from deck import courtkit as K
from deck.motifs import core as C
import shapely
from shapely.geometry import LineString
sc = m.figure()
items = {i.name: i for i in sc.items}
band = K.box(0, 511 - K.MEDIUM / 2, 2000, 600)
for cuff, hand in (('cuffL', 'handL'), ('cuffR', 'handR')):
    it = items[cuff]
    reg = it.occ
    ol = reg.boundary.buffer(K.MEDIUM / 2)
    hs = items[hand].occ.boundary.buffer(K.MEDIUM / 2)
    marks = [mk for mk in it.frag.marks if mk.layer == 'ink']
    parts = []
    for mk in marks:
        r = mk.role.split('@')[0]
        if r == 'stem':
            for pts, _closed in C.sample_d(mk.d, 0.3):
                ln = LineString(pts)
                L = ln.length
                if L > 17:
                    core = shapely.ops.substring(ln, 8.0, L - 8.0)
                    parts.append(core.buffer(mk.w / 2))
        elif r in ('volute', 'leaf', 'terminal', 'petiole'):
            parts.append(C.Frag([mk]).shape())
    sp = shapely.union_all(parts).intersection(K.box(0, 0, 2000, 511))
    print(f'{cuff}: sprig→cuff outline {sp.distance(ol):.2f}  →hand outline {sp.distance(hs):.2f}  →band rule {sp.distance(band):.2f}')
