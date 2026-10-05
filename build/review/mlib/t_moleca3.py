from rh import *
from deck.motifs import lion as LI
from deck.motifs.sheet_figurative import spade_live
f = LI.lion_moleca(375, 262, silhouette=spade_live())
show(f, "moleca-chest-specks-10x", zoom=10, ground=T.PAPER, under=[(spade_live(), T.INK)], view=(335, 290, 415, 345))
