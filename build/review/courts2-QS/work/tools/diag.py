"""diag: build QS scene, compose, print heal log entries in a window, and hand warnings."""
import sys, warnings, importlib
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
from deck import courtkit as K
import art.QS as Q
win = None
if len(sys.argv) > 1:
    win = tuple(float(v) for v in sys.argv[1].split(','))
K.HAND_LOG.clear()
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    sc = Q.figure()
    res = Q.compose_scene(sc)
print('HAND_LOG:', K.HAND_LOG)
for e in sc.heal_log:
    s = str(e)
    if win is None:
        print(s[:300])
    else:
        import re
        where = e.get('where') if isinstance(e, dict) else None
        if where is None:
            print(s[:300]); continue
        x, y = where[0], where[1]
        if win[0] <= x <= win[2] and win[1] <= y <= win[3]:
            print(s[:300])
print('n heal', len(sc.heal_log))
print('items', [it.name for it in sc.items])
