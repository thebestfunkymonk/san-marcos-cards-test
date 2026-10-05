import sys, os
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import warnings
import QC
from deck import courtkit as K
from shapely.geometry import Point
sc, fc = QC.figure()
res = QC.Q.compose(sc)
print("items:", [it.name for it in sc.items])
for e in sc.heal_log:
    print("heal:", e)
print("HAND_LOG:", K.HAND_LOG)
