import sys; sys.path.insert(0,'.')
from art import JH as M
sc = M.figure()
for it in sc.items:
    if it.occ is not None and not it.occ.is_empty:
        print(f"{it.name:14s}", [round(v,1) for v in it.occ.bounds])
