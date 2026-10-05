import sys, warnings
warnings.simplefilter("ignore")
sys.path.insert(0, ".")
from deck import courtkit as K
from art import KD
sc = KD.figure()
sc.layers()
for h in sc.heal_log: print("  ", h)
print("HAND_LOG:", getattr(K, "HAND_LOG", None))
