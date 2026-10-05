import sys, collections
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import art.KH as KH
sc = KH.figure(); sc.compose()
c = collections.Counter()
for e in sc.heal_log:
    c[(e["action"], e["role"], tuple(e.get("near", [])))] += 1
for e in sc.heal_log:
    print(e)
print(len(sc.heal_log))
