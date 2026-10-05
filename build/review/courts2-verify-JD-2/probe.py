import sys, os, math, warnings
sys.path.insert(0, 'art')
warnings.simplefilter('ignore')
from deck import courtkit as K
import JD, _jd_hands as H
sc = JD.figure()
print('HAND_LOG', K.HAND_LOG)
for it in sc.items:
    if it.name.startswith('hand') or it.name.startswith('cuff') or it.name in ('map',):
        print(it.name, type(it).__name__, [a for a in dir(it) if not a.startswith('_')][:30])
        break
