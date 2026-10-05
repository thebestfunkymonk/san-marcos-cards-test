import sys, os
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/art')
import JC
from deck import courtkit as K
JC.PADDLE_HALO_ONLY=("jerkin", "armR", "doublet"); JC.BELT_SKIP_R=(0,0,1,1)
build = JC.build
figure = JC.figure
