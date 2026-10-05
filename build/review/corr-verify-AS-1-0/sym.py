import sys
sys.path.insert(0, '.')
import shapely
from shapely import affinity
from deck import qa as Q
for name, path, ylim in [('before', 'build/gallery/svg/AS.svg', 548), ('after', 'cards/AS.svg', 640)]:
    pieces = Q.card_geometry(open(path).read())
    art = [p for p in pieces if p['art']]
    up = shapely.union_all([p['geom'] for p in art if p['geom'].bounds[3] < ylim])
    M = affinity.scale(up, -1, 1, origin=(375, 0))
    sd = up.symmetric_difference(M)
    print(name, 'above legend: area', round(up.area,1), 'mirror symdiff', round(sd.area, 2), 'hausdorff', round(up.hausdorff_distance(M), 3))
    # by band
    for lab, (y0, y1) in {'waterline': (ylim-200, ylim-190)}.items():
        pass
    # component groups
    import collections
    groups = collections.defaultdict(list)
    for p in art:
        b = p['geom'].bounds
        cx = (b[0]+b[2])/2
        if b[2] < 130 or b[0] > 620: groups['columns'].append(p['geom'])
        elif b[1] >= ylim and (p['kind'] == 'stroke'): groups['emrules'].append(p['geom'])
    for k, gs in groups.items():
        u = shapely.union_all(gs); m = affinity.scale(u, -1, 1, origin=(375, 0))
        print('  ', k, len(gs), 'symdiff', round(u.symmetric_difference(m).area, 3), 'hausdorff', round(u.hausdorff_distance(m), 3), 'bounds', tuple(round(v, 2) for v in u.bounds))
    # waterline: pieces with small height outside spade, y around 350/442
    wl = [p['geom'] for p in art if p['kind']=='stroke' and (p['geom'].bounds[3]-p['geom'].bounds[1]) < 5 and p['geom'].bounds[1] < ylim and (p['geom'].bounds[2] < 221 or p['geom'].bounds[0] > 529)]
    u = shapely.union_all(wl); m = affinity.scale(u, -1, 1, origin=(375, 0))
    print('   waterline', len(wl), 'symdiff', round(u.symmetric_difference(m).area, 3), 'bounds', tuple(round(v, 2) for v in u.bounds))
    for g in sorted(wl, key=lambda g: g.bounds[0]): print('      dash', tuple(round(v,2) for v in g.bounds))
