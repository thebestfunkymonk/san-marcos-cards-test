import sys
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
from deck import qa as Q
Q._clusters.__defaults__ = (999,)
for path in sys.argv[1:]:
    txt = open(path).read()
    r = Q.raster_checks({'kind': 'court', 'svg': path, 'suit': 'C', 'color': 'black', 'status': 'art'}, txt)
    fl = r['_raster12']
    tot = 0
    print(path)
    for L, v in fl.items():
        for k in ('thin', 'gaps'):
            top = [c for c in v[k] if c['bbox'][1] < 525]
            tot += len(top)
            for c in sorted(top, key=lambda c: (c['bbox'][1], c['bbox'][0])):
                print(f"  {L:5} {k:5} {c['bbox']} {c['area']}")
    print('  TOTAL (top half):', tot, ' balance', r['5']['balance'])
