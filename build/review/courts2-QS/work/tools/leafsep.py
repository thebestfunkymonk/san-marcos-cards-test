import sys
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
import numpy as np
from shapely.geometry import Point
from deck import courtkit as K
import art.QS as Q
from art import _qs_parts as QP
hand = K.fist(Q.FIST_L, Q.POSY["axis_deg"], wrist=Q.WRIST_L, wrist_w=24.0, hand="R", **Q.HAND_L).hand.shape
mouth = np.array(Q.POSY['mouth'])
for l3 in (-160, -157, -154, -151):
    for rh in (158, 160):
        lv = (Q.LEAVES[0], Q.LEAVES[1], (float(l3), 56.0, 6.0))
        po = QP.laurel_posy(mouth, Q.POSY['axis_deg'], holder_len=Q.POSY_LEN, leaves=lv, raceme=(float(rh),) + Q.RACEME[1:])
        rl = po['raceme'].lines.shape()
        ll = po['leaves'].lines.shape()
        away = Point(*mouth).buffer(9.0)
        d = rl.difference(away).distance(ll.difference(away))
        dl = po['leaves'].shape.distance(hand)
        fl = min(f.distance(hand) for f in po['raceme'].meta['florets'])
        # leaf-leaf: third vs second leaf
        print(l3, rh, 'raceme-ink vs leaf-ink (outside mouth r9):', round(d, 2), ' floret-hand', round(fl, 1))
