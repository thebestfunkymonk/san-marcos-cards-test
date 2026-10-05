import sys, time
sys.path.insert(0, '.')
t=time.time()
from art import QH
sc = QH.figure(); t1=time.time(); print('figure', t1-t)
L = sc.layers(); t2=time.time(); print('layers', t2-t1, type(L))
print(len(sc.heal_log))
for e in sc.heal_log[:80]:
    print(e)
