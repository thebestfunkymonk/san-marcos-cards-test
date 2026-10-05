import sys, os
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/art')
import JC
from deck import courtkit as K
JC.FIST=(548.0, 400.0); JC.WR = tuple(K.fist_wrist(JC.FIST, -90.0, bend=40.0, dist=1.1, **JC.FIST_KW)); JC.SLEEVE_R_SPEC["wrist_w"]=34.0
build = JC.build
figure = JC.figure
