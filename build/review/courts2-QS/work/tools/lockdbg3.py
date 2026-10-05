import sys
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
import numpy as np
from shapely.geometry import LineString, Point
from inkkit import geom as G
from deck import courtkit as K
import art.QS as Q
from art import _qs_parts as QP
posy = Q.posy_parts()
handL = K.fist(Q.FIST_L, Q.POSY["axis_deg"], wrist=Q.WRIST_L, wrist_w=24.0, hand="R", **Q.HAND_L)
front = K.U(posy["holder"].shape, posy["leaves"].shape, posy["raceme"].shape, handL.hand.shape)
fr = QP.rot_geom(front.buffer(K.HALO, quad_segs=8), -Q.TILT, Q.PIVOT)
hg = Q.head_group(front=fr)
lf = QP.rot_part(hg['lf'], Q.TILT, Q.PIVOT)
halo = posy['leaves'].shape.buffer(K.HALO + K.MEDIUM/2)
for m in lf.lines.marks:
    if m.role == 'current':
        for pts, _ in G.as_polys(m.d, 0.1):
            pts = np.asarray(pts)
            e = Point(*pts[-1])
            print('end', pts[-1].round(1), 'dist to leaf halo', round(e.distance(halo),1), 'to leaves', round(e.distance(posy['leaves'].shape),1))
