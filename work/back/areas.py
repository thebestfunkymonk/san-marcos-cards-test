import sys, time
sys.path.insert(0, '.')
from art import BACK
from art import _back_frame as BF
FLOOD = 675*975 - (4-3.14159)*18*18
p = BACK.parts()
tot = 0
for k, f in p.items():
    a = f.shape().area
    tot += a
    print(f"{k:10s} {a:9.0f}  {a/FLOOD*100:5.2f}%")
print('sum', tot/FLOOD*100)
