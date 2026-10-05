import sys, os
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/art')
import JC
from deck import courtkit as K
JC.HAND_L.update(length=58.0, width=33.0, curl=8.0, thumb_deg=46.0, thumb_len=0.42, tips=(5.0,0.0,3.0,9.0), knuckle=0.48); JC.HAND_L_ANGLE=40.0; JC.HAND_L_KW=dict(crease="web", ulnar_r=5.0, crease_len=0.24, crease_sag=1.0); JC.PADDLE_HALO_ONLY=("jerkin","armR","doublet","belt"); JC.DROP_HEEL_POCKET=True; JC.FOREARM_R_SPRAY="M485 506L501 462"
build = JC.build
figure = JC.figure
