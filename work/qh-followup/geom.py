import sys, importlib
sys.path.insert(0, '.')
import shapely
from art import QH
sc = QH.figure()
for it in sc.items:
    if it.occ is not None and not it.occ.is_empty:
        b = it.occ.bounds
        if b[2] > 420 and b[1] < 360:
            print(f"{it.name:16s} {b[0]:6.1f} {b[1]:6.1f} {b[2]:6.1f} {b[3]:6.1f}")
