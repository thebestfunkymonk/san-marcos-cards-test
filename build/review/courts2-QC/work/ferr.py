import sys, os
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import QC
from deck import courtkit as K
import numpy as np
def check(root_dy=8.0, ferrule=(13.0, 7.5), w_root=None, neck=36.0):
    kw = dict(QC.FAN_KW)
    if w_root: kw['w_root'] = w_root
    parts = dict(QC.FN.fan(QC.FIST_L, QC.FAN_AXIS, QC.PLUMES, root_dy=root_dy, ferrule=ferrule, neck=neck, **kw))
    fer = parts['ferrule'].shape
    ring = fer.buffer(4.7).difference(fer)
    union = K.U(*[parts[f'plume{i}'].shape for i in range(5)])
    out = []
    for i in range(5):
        b = parts[f'plume{i}'].shape.boundary
        # visible part of plume i's boundary: not covered by later plumes (in front) or the ferrule
        front = K.U(*[parts[f'plume{j}'].shape for j in range(i+1, 5)]) if i < 4 else None
        vis = b.difference(fer)
        if front is not None: vis = vis.difference(front)
        near = vis.intersection(ring)
        out.append(round(near.length, 1))
    return out
print('base', check())
for rd in (10.0, 12.0):
    print('root_dy', rd, check(root_dy=rd))
for fr in ((13.0, 8.5), (14.0, 8.0), (12.0, 7.5)):
    print('ferrule', fr, check(ferrule=fr))
print('w_root 6', check(w_root=6.0))
