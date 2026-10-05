import sys, warnings, importlib.util, os
sys.path.insert(0, '.')
path = 'art/JH.py'
spec = importlib.util.spec_from_file_location('jhmod', path)
m = importlib.util.module_from_spec(spec); sys.path.insert(0, os.path.dirname(os.path.abspath(path))); spec.loader.exec_module(m)
from deck import courtkit as K
K.HAND_LOG.clear()
with warnings.catch_warnings(record=True) as ws:
    warnings.simplefilter('always')
    sc = m.figure()
    m.compose(sc)
for w in ws:
    if 'Hand' in type(w.message).__name__ or 'hand' in str(w.message): print('WARN', w.message)
print('HAND_LOG', K.HAND_LOG)
if '-v' in sys.argv:
    for it in sc.items:
        if it.occ is not None and not it.occ.is_empty:
            print(f"{it.name:22s} {tuple(round(v,1) for v in it.occ.bounds)}")
print('heal entries', len(sc.heal_log))
for e in sc.heal_log:
    print(' ', e)
