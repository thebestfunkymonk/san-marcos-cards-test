"""dbgv.py <variant module path> [x y r]... : heal log entries within r of points, and hand warnings."""
import sys, os, warnings, importlib.util
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'art'))
from deck import courtkit as K
spec = importlib.util.spec_from_file_location('v', sys.argv[1]); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
with warnings.catch_warnings(record=True) as ws:
    warnings.simplefilter('always')
    sc = mod.figure(); sc.compose()
for w in ws: print('WARN', w.message)
args = [float(a) for a in sys.argv[2:]]
pts = [(args[i], args[i+1], args[i+2]) for i in range(0, len(args), 3)]
print('heal entries', len(sc.heal_log))
for e in sc.heal_log:
    x, y = e['at']
    if not pts or any((x-px)**2 + (y-py)**2 <= r*r for px, py, r in pts):
        print('HEAL', e['action'], e['role'], e['layer'], e['at'], e['why'], e.get('near'))
