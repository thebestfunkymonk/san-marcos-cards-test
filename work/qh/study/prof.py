import time, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
t=time.time()
from art import QH
sc = QH.figure()
t1=time.time(); print("figure", round(t1-t,1))
import deck.courtkit as K
orig_heal = K.heal
def timed_heal(*a, **k):
    t=time.time(); r=orig_heal(*a, **k); print("heal", round(time.time()-t,1)); return r
K.heal = timed_heal
f = sc.compose()
t2=time.time(); print("compose", round(t2-t1,1), "marks", len(f.marks), "heal log", len(sc.heal_log))
from collections import Counter
print(Counter(e['action'] for e in sc.heal_log))
print(Counter((e['role'],e['action']) for e in sc.heal_log).most_common(15))
print([e for e in sc.heal_log if e['action']=='UNRESOLVED'][:10])
