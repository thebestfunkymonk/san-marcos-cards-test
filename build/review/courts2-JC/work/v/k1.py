import sys, os
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/art')
import JC
from deck import courtkit as K
JC.JERK_R_LOW=[(512,540),(510,470),(504,428)]; JC.FIST=(548.0, 404.0); JC.WR = tuple(K.fist_wrist(JC.FIST, -90.0, bend=40.0, dist=0.9, **JC.FIST_KW))
build = JC.build
figure = JC.figure
