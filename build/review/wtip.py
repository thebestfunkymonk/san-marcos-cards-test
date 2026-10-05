import sys; sys.path.insert(0,"build/review"); sys.path.insert(0,".")
from rend import out
from deck.motifs import rice as R
f = R.rice_wreath_arc(0,0,150)
out(f, "wreath-lefttip-10x", (-186, 44, -160, 64), 10)
out(f.mirror_x(0), "wreath-righttip-mirrored-10x", (-186, 44, -160, 64), 10)
