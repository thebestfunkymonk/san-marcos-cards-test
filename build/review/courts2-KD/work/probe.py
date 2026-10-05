import sys, json, warnings
sys.path.insert(0, '.')
warnings.simplefilter('ignore')
import importlib.util
path = sys.argv[1] if len(sys.argv) > 1 else 'art/KD.py'
spec = importlib.util.spec_from_file_location('kdprobe', path)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from deck import courtkit as K
K.HAND_LOG.clear()
sc = m.figure()
sc.compose() if hasattr(sc, 'compose') else None
print('HAND_LOG', K.HAND_LOG)
log = sc.heal_log
print('heal entries', len(log))
for e in log:
    s = json.dumps(e, default=str)
    print(s[:220])
