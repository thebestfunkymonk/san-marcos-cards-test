import sys
from inkkit import geom as G
from art import _back_frame as BF
import numpy as np
f = BF.rules()
print('ROUNDEL_C', BF.ROUNDEL_C)
rows=[]
for m in f.marks:
    for p,_ in G.flatten(m.d, 0.05):
        P=np.asarray(p)
        if len(P)<2: continue
        a,b=P[0],P[-1]
        # only TL quadrant ends
        for e in (a,b):
            if e[0]<200 and e[1]<200:
                rows.append((m.w, round(float(e[0]),2), round(float(e[1]),2)))
for r in sorted(set(rows)): print(r)
