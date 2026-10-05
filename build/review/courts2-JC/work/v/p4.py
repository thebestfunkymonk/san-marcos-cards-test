import sys, os
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/art')
import JC
from deck import courtkit as K
JC.PLUME_KW['lines']=((3.6, 36.0, -52.0, 0), (-3.6, 40.0, -30.0, +1))
build = JC.build
figure = JC.figure
