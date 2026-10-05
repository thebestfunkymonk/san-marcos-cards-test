import sys, itertools
sys.path.insert(0, '.'); sys.path.insert(0, 'art')
import JD
from deck import courtkit as K
from deck.motifs import core as C
import shapely
from shapely.geometry import LineString
band = K.box(0, 511 - K.MEDIUM / 2, 2000, 600)
def measure(sc):
    items = {i.name: i for i in sc.items}
    it = items['cuffL']; ol = it.occ.boundary.buffer(K.MEDIUM / 2); hs = items['handL'].occ.boundary.buffer(K.MEDIUM / 2)
    parts, have = [], set()
    for mk in it.frag.marks:
        if mk.layer != 'ink': continue
        r = mk.role.split('@')[0]
        if r == 'stem':
            for pts, _ in C.sample_d(mk.d, 0.3):
                ln = LineString(pts)
                if ln.length > 17: parts.append(shapely.ops.substring(ln, 8.0, ln.length - 8.0).buffer(mk.w / 2))
        elif r in ('volute', 'leaf', 'terminal', 'petiole'):
            parts.append(C.Frag([mk]).shape()); have.add(r)
    sp = shapely.union_all(parts).intersection(K.box(0, 0, 2000, 511))
    return sp.distance(ol), sp.distance(hs), sp.distance(band), sorted(have)
dy = float(sys.argv[1]); bend = float(sys.argv[2])
JD.FIST_L = (260.5, 460.0 + dy); JD.MAP = (262.0, 362.0, 434.0 + dy, 492.0 + dy); JD.BEND_L = bend
for xf, yc, r0 in itertools.product(*[list(map(float, a.split(','))) for a in sys.argv[3:6]]):
    JD.CUFF_SPRIG_L = dict(JD.CUFF_SPRIG, x_first=xf, yc=yc, r0=r0)
    sc = JD.figure()
    o, h, b, have = measure(sc)
    print(f'dy {dy} bend {bend} x_first {xf} yc {yc} r0 {r0}: outline {o:.2f} hand {h:.2f} band {b:.2f} {have}', flush=True)
