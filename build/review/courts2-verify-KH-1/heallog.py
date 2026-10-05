import sys, json
sys.path.insert(0, '.')
from art import KH
from deck import courtkit as K
sc = KH.figure()
sc.layers()
log = sc.heal_log
print(len(log), "heal entries")
for e in log:
    print(e)
print("HAND_LOG", getattr(K, "HAND_LOG", None))
