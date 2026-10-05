import sys, os
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/art')
import JC
from deck import courtkit as K
JC.HAND_L.update(length=56.0, width=32.0, curl=14.0, thumb_deg=36.0, thumb_len=0.38, tips=(5.0,0.0,3.0,9.0), knuckle=0.48); JC.HAND_L_ANGLE=30.0; JC.HAND_L_KW=dict(crease="web", ulnar_r=5.0)
build = JC.build
figure = JC.figure
