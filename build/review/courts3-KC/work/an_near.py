import sys; sys.path.insert(0,'.')
import numpy as np, json, shapely
from shapely.geometry import Point, box
from deck import courtkit as K
from art import KC
opts = json.loads(sys.argv[1]); bx = box(*map(float, sys.argv[2:6]))
roles = sys.argv[6].split(',') if len(sys.argv) > 6 else None
sc = KC.figure(opts)
stage = sys.argv[7] if len(sys.argv) > 7 else 'raw'
if stage == 'raw':
    it = [i for i in sc.items if i.name == 'robe'][0]
    marks = it.frag.marks
else:
    marks = sc.compose(heal_gaps=(stage=='healed')).marks
for m in marks:
    if m.kind == 'fill' or not m.d: continue
    r = m.role.split('@')[0]
    if roles and r not in roles: continue
    for ln in K._stroke_lines(m.d):
        g = ln.intersection(bx)
        if g.is_empty: continue
        c = np.asarray(ln.coords)
        print(r, m.w, np.round(c[0],1).tolist(), np.round(c[-1],1).tolist(), 'len %.1f' % ln.length)
for it in sc.items:
    if it.occ is not None and not it.occ.is_empty and it.occ.intersects(bx):
        print('ITEM', it.name, 'halo', it.halo, it.halo_only)
