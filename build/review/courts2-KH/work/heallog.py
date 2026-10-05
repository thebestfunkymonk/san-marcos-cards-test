import sys, warnings, importlib
sys.path.insert(0, '.')
warnings.simplefilter('always')
from deck import courtkit as K
mod = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else 'art.KH')
sc = mod.figure()
sc.layers()
for e in sc.heal_log:
    print(e)
print('HAND_LOG', K.HAND_LOG)
