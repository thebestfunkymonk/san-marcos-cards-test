import sys, importlib.util
sys.path.insert(0, '.'); sys.path.insert(0, 'art')
pid = sys.argv[1]
spec = importlib.util.spec_from_file_location(pid, f'art/{pid}.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure(); sc.compose()
bb = [float(v) for v in sys.argv[2].split(',')] if len(sys.argv) > 2 else [0,0,1e9,1e9]
n = 0
for e in sc.heal_log:
    x, y = e.get('at', [0, 0])
    if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3]:
        print(e); n += 1
print('total', len(sc.heal_log), 'in box', n)
