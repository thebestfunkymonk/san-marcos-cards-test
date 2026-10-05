import numpy as np
from art import JH
from deck import courtkit as K
from shapely.geometry import LineString
sc = JH.figure()
it = {i.name: i for i in sc.items}
cuff=it["cuffR"].occ; body=it["fiddle-body"].occ
for x in range(536, 572, 3):
    v = LineString([(x, 250), (x, 340)])
    cb = v.intersection(cuff); bb = v.intersection(body)
    cy = max(c[1] for c in cb.coords) if not cb.is_empty else None
    by = min(c[1] for g in getattr(bb,'geoms',[bb]) for c in g.coords) if not bb.is_empty else None
    print(x, "cuff bottom", None if cy is None else round(cy,1), "body top", None if by is None else round(by,1), "gap(+)/overlap(-)", None if (cy is None or by is None) else round(by-cy,1))
