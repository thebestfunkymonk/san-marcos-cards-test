import sys
sys.path.insert(0, '.')
import shapely, numpy as np
from shapely import affinity
from deck import qa as Q
for name, path in [('before', 'build/gallery/svg/AS.svg'), ('after', 'cards/AS.svg')]:
    pieces = Q.card_geometry(open(path).read())
    art = [p for p in pieces if p['art']]
    idx = [p for p in pieces if p['cls'] & Q.INDEX_CLASSES]
    tl = shapely.union_all([p['geom'] for p in idx if p['geom'].centroid.y < 525])
    br = shapely.union_all([p['geom'] for p in idx if p['geom'].centroid.y > 525])
    U = shapely.union_all([p['geom'] for p in art])
    b = U.bounds
    print(f'== {name}: art pieces {len(art)} idx {len(idx)}; vector bounds x {b[0]:.2f}-{b[2]:.2f} y {b[1]:.2f}-{b[3]:.2f} mid ({(b[0]+b[2])/2:.2f},{(b[1]+b[3])/2:.2f})')
    print(f'   safe margins L {b[0]-37.5:.2f} R {712.5-b[2]:.2f} T {b[1]-37.5:.2f} B {1012.5-b[3]:.2f}')
    for lab, z in (('TL', tl), ('BR', br)):
        ds = sorted(((shapely.distance(p['geom'], z), p) for p in art), key=lambda t: t[0])[:4]
        print(f'   {lab} index bounds {tuple(round(v,1) for v in z.bounds)}; nearest:', [(round(d,2), tuple(round(v,1) for v in p['geom'].bounds), p.get('cls')) for d, p in ds])
    # symmetry of the art union excluding type (fills in the legend region y>= legend top)
    G = [p['geom'] for p in art]
    Ug = shapely.union_all(G)
    M = affinity.scale(Ug, -1, 1, origin=(375, 0))
    diff = Ug.symmetric_difference(M)
    print('   mirror symdiff area (all art):', round(diff.area, 1))
