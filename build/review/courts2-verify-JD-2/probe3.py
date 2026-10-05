import sys, warnings, itertools
sys.path.insert(0, 'art'); warnings.simplefilter('ignore')
from deck import courtkit as K
from deck.motifs import core as C
import shapely
from shapely.geometry import LineString, Point
import JD
sc = JD.figure()
items = {i.name: i for i in sc.items}
def lines(mk):
    out=[]
    for pts, closed in C.sample_d(mk.d, 0.2):
        out.append(LineString(pts))
    return shapely.union_all(out)
for h in ('handR','handL'):
    it = items[h]
    ms = [(m.role, lines(m), m.w) for m in it.frag.marks]
    print('==', h, 'widths', sorted(set(round(m.w,2) for m in it.frag.marks)))
    fingers = [x for x in ms if x[0]=='finger']
    thumb = [x for x in ms if x[0]=='thumb'][0]
    outl = [x for x in ms if x[0]=='outline'][0]
    for (r1,g1,w1),(r2,g2,w2) in itertools.combinations(fingers,2):
        print(f'  finger-finger gap {g1.distance(g2)-(w1+w2)/2:.2f}')
    for i,(r,g,w) in enumerate(fingers):
        print(f'  finger{i} len {g.length:.1f} → thumb gap {g.distance(thumb[1])-(w+thumb[2])/2:.2f}  → outline gap(nonzero?) {g.distance(outl[1])-(w+outl[2])/2:.2f}')
    print(f'  thumb len {thumb[1].length:.1f}')
    # parallel check: thumb line vs finger0 min distance excluding touching ends
    occ = it.occ
    print('  hand occ bounds', [round(v,1) for v in occ.bounds], 'area', round(occ.area,1))
    # distances between finger line ends and the hand outline
    for i,(r,g,w) in enumerate(fingers):
        cs = list(g.geoms[0].coords) if hasattr(g,'geoms') else list(g.coords)
        a, b = Point(cs[0]), Point(cs[-1])
        print(f'  finger{i} ends {tuple(round(v,1) for v in cs[0])}->{tuple(round(v,1) for v in cs[-1])}  end→outline {a.distance(outl[1]):.2f} {b.distance(outl[1]):.2f}')
# face size
head = [i for i in sc.items if i.name=='head'][0]
print('head occ bounds', [round(v,1) for v in head.occ.bounds])
