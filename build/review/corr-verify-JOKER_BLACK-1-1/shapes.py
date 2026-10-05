import re, sys, math
import numpy as np, shapely
from shapely.geometry import box, Point
sys.path.insert(0, '.')
from inkkit import geom as G

def load(fn):
    t = open(fn).read()
    layers = {}
    for m in re.finditer(r'<g id="(\w+)"[^>]*>(.*?)</g>', t, re.S):
        lid, body = m.group(1), m.group(2)
        items = []
        for p in re.finditer(r'<path ([^>]*)/>', body):
            a = p.group(1)
            d = re.search(r' d="([^"]*)"', ' '+a).group(1)
            fill = re.search(r'fill="([^"]*)"', a); fill = fill.group(1) if fill else None
            sw = re.search(r'stroke-width="([^"]*)"', a); sw = float(sw.group(1)) if sw else None
            cls = re.search(r'class="([^"]*)"', a); cls = cls.group(1) if cls else ''
            lc = re.search(r'stroke-linecap="([^"]*)"', a); lc = lc.group(1) if lc else 'butt'
            items.append(dict(d=d, fill=fill, sw=sw, cls=cls, cap=lc))
        layers[lid] = items
    return layers

def shape_of(it):
    if it['fill'] and it['fill'] != 'none':
        return G.to_shape(it['d'], tol=0.02)
    else:
        cap = {'butt': 'flat', 'round': 'round', 'square': 'square'}[it['cap']]
        polys = G.flatten(it['d'], tol=0.02)
        lines = [shapely.LineString(p) if not c else shapely.LinearRing(p) for p, c in polys]
        return shapely.union_all([l.buffer(it['sw']/2, cap_style=cap, join_style='mitre', mitre_limit=4) for l in lines])

if __name__ == '__main__':
    fn = sys.argv[1]
    L = load(fn)
    for k, v in L.items():
        print(k, len(v), sorted(set(i['sw'] for i in v if i['sw'])), sorted(set(i['fill'] for i in v if i['fill'])), set(i['cls'] for i in v))
