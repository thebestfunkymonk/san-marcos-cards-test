import sys; sys.path.insert(0, '.')
import importlib
QH = importlib.import_module('art.QH')
bb = tuple(map(float, sys.argv[1:5])) if len(sys.argv) > 4 else None
sc = QH.figure()
res = sc.compose()
n = 0
for e in sc.heal_log:
    at = e.get('at') if isinstance(e, dict) else None
    if bb is None or (at and bb[0] <= at[0] <= bb[2] and bb[1] <= at[1] <= bb[3]):
        print({k: (round(v, 1) if isinstance(v, float) else v) for k, v in e.items()} if isinstance(e, dict) else e)
        n += 1
print('total', len(sc.heal_log), 'shown', n)
