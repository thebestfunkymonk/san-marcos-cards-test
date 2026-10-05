import sys
sys.path.insert(0, 'build/review/corr-verify-JOKER_BLACK-2-1'); sys.path.insert(0, '.')
import shapely
from shapely.geometry import box
from shapes import load, shape_of
for fn in ['cards/JOKER-BLACK.svg', 'cards/JOKER-RED.svg']:
    L = load(fn)
    fig = []; cap = []
    for lid, items in L.items():
        if lid == 'paper': continue
        for it in items:
            if 'index' in it['cls'] or 'stock' in it['cls']: continue
            s = shape_of(it)
            (cap if (s.bounds[1] > 740 or 'joker' in it['cls']) else fig).append((lid, s))
    F = shapely.union_all([s for _, s in fig]); C = shapely.union_all([s for _, s in cap])
    print(fn, 'figure bounds', [round(v,2) for v in F.bounds], 'caption bounds', [round(v,2) for v in C.bounds])
    print('   gap figure bottom -> rule centre 762:', round(762 - F.bounds[3],2), ' -> rule top edge 761:', round(761-F.bounds[3],2), ' -> caption top', round(C.bounds[1]-F.bounds[3],2))
    print('   vector block middle', round((F.bounds[1]+C.bounds[3])/2,2), 'figure area centroid', round(F.centroid.x,2), round(F.centroid.y,2))
    idx = shapely.union_all([shape_of(it) for it in L['ink'] if 'index' in it['cls']])
    print('   min dist figure -> index', round(F.distance(idx),2), ' caption->index', round(C.distance(idx),2))
    zone = box(0,0,130,310).union(box(620,740,750,1050))
    print('   figure in index zone area', round(F.intersection(zone).area,3))
    # lowest pieces
    lows = sorted(fig, key=lambda t: -t[1].bounds[3])[:3]
    for lid, s in lows: print('   low piece', lid, [round(v,2) for v in s.bounds])
