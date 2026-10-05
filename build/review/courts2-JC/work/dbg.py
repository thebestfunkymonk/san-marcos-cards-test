"""dbg.py [x y ...] : compose art/JC.py, print heal log (optionally near points) and items at points."""
import sys, os, warnings
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'art'))
from shapely.geometry import Point
from deck import courtkit as K
K.HAND_LOG.clear()
import importlib; JC = importlib.import_module('JC')
with warnings.catch_warnings(record=True) as ws:
    warnings.simplefilter('always')
    sc = JC.figure(); sc.compose()
    for w in ws: print('WARN', w.message)
print('HAND_LOG', K.HAND_LOG)
pts = [(float(sys.argv[i]), float(sys.argv[i+1])) for i in range(1, len(sys.argv)-1, 2)]
for e in sc.heal_log:
    print('HEAL', e)
for p in pts:
    print('--- at', p)
    for it in sc.items:
        if it.occ is not None and not it.occ.is_empty and it.occ.distance(Point(*p)) < 3:
            print('   ', it.name, 'contains' if it.occ.contains(Point(*p)) else 'near', 'halo', it.halo)
