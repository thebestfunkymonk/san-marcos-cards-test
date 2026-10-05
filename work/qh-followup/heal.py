import sys
sys.path.insert(0, '.')
from art import QH
sc = QH.figure()
L = sc.layers()
n = 0
for e in sc.heal_log:
    at = e.get('at')
    if at and 470 <= at[0] <= 535 and 55 <= at[1] <= 320 or 'bubble' in str(e.get('role')):
        print(e); n += 1
print('total heal', len(sc.heal_log), 'near ribbon', n)
