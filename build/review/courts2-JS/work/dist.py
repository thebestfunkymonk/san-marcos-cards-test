import sys, os, importlib.util
sys.path.insert(0, '.')
path = sys.argv[1]
spec = importlib.util.spec_from_file_location("v", path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
items = {it.name: it for it in sc.items}
pairs = [p.split(':') for p in sys.argv[2:]]
for a, b in pairs:
    A, B = items[a].occ, items[b].occ
    print(a, b, 'dist', round(A.distance(B), 2), 'overlap', round(A.intersection(B).area, 1))
print('W', [round(v,1) for v in m.WRIST_R], 'F', [round(v,1) for v in m.FIST_R])
