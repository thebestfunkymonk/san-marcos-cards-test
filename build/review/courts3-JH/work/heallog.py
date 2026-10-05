# heallog.py [pkgroot] -> prints heal log of art.JH from pkgroot (default: project)
import sys, os, warnings
root = sys.argv[1] if len(sys.argv) > 1 else '.'
sys.path.insert(0, '.')
sys.path.insert(0, root)
import importlib
m = importlib.import_module('art.JH')
print('# from', m.__file__, file=sys.stderr)
from deck import courtkit as K
sc = m.figure()
if hasattr(m, 'compose'): m.compose(sc)
else: sc.compose()
for e in sc.heal_log:
    print(e['action'], e['role'], e['layer'], e['at'], e['why'][:40], e.get('near'))
