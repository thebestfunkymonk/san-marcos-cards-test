import sys, os
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/art')
import JC
from deck import courtkit as K
JC.FIST=(548.0, 412.0); JC.WR = tuple(K.fist_wrist(JC.FIST, -90.0, bend=45.0, dist=1.0, **JC.FIST_KW))
build = JC.build
figure = JC.figure
