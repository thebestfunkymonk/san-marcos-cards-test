import sys, importlib.util, json
sys.path.insert(0,'.')
path = sys.argv[1] if len(sys.argv)>1 else 'art/KC.py'
spec = importlib.util.spec_from_file_location('kcmod', path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from deck import courtkit as K
K.HAND_LOG.clear()
sc = m.KC.figure(m.OPTS) if hasattr(m, "OPTS") else m.figure()
sc.compose()
for e in sc.heal_log:
    print(e)
print('HAND_LOG', K.HAND_LOG)
