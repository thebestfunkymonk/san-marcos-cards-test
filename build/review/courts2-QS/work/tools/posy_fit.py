import sys
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
import numpy as np
from deck import courtkit as K
import art.QS as Q
from art import _qs_parts as QP
hand = K.fist(Q.FIST_L, Q.POSY["axis_deg"], wrist=Q.WRIST_L, wrist_w=24.0, hand="R", **Q.HAND_L).hand.shape
u = K.unit(Q.POSY['axis_deg'])
foot = np.array(Q.POSY['mouth']) - u*33.0
for L in (38, 39, 40):
    mouth = foot + u*L
    for hd in (155, 157, 159, 161):
        po = QP.laurel_posy(mouth, Q.POSY['axis_deg'], holder_len=L,
                            leaves=((-70.0, 58.0, 5.0), (-118.0, 62.0, -6.0), (-160.0, 56.0, 6.0)),
                            raceme=(hd, 64.0, -8.0, 5, 6.6))
        fl = po['raceme'].meta['florets']
        d = min(f.distance(hand) for f in fl)
        dl = po['raceme'].shape.distance(po['leaves'].shape)
        print(L, hd, 'floret-hand', round(d,1), 'raceme-leaves', round(dl,1), 'mouth', mouth.round(1))
