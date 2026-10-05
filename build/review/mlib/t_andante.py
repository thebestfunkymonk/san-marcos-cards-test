from rh import *
from deck.motifs import lion as LI
f = LI.lion_andante(0, 0)
show(f, "andante-4x", zoom=4, ground=T.BOARD, view=(-170,-225,170,225))
show(f, "andante-head-8x", zoom=8, ground=T.BOARD, view=(-160,-130,-20,40))
print(f.meta.get("warnings"))
