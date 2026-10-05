import re, sys
from xml.etree import ElementTree as ET
sys.path.insert(0, '.')
from inkkit import geom as G
NS = '{http://www.w3.org/2000/svg}'
def load(p):
    t = ET.parse(p).getroot()
    out = []
    for g in t.iter(NS+'g'):
        for el in g:
            if el.tag == NS+'path':
                a = dict(el.attrib); d = a.pop('d')
                out.append((g.get('id'), a, d))
    return out
A = load(sys.argv[1]); B = load(sys.argv[2])
print(len(A), len(B))
for i, ((la, aa, da), (lb, ab, db)) in enumerate(zip(A, B)):
    try:
        ba = G.bbox(da); bb = G.bbox(db)
    except Exception as e:
        ba = bb = None
    same_attr = aa == ab
    dy = None
    if ba and bb:
        dys = [bb[1]-ba[1], bb[3]-ba[3]]; dxs = [bb[0]-ba[0], bb[2]-ba[2]]
    print(i, la, lb, aa.get('class',''), aa.get('stroke-width', ''), 'attr_same' if same_attr else f'ATTR DIFF {aa} vs {ab}',
          'len', len(da), len(db),
          'bboxA', tuple(round(v,1) for v in ba) if ba else None, 'dx', [round(v,2) for v in dxs] if ba else None, 'dy', [round(v,2) for v in dys] if ba else None)
