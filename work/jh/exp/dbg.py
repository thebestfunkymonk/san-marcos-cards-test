import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jh/exp")
from render import render
from art import _jh_face as JF
from deck import courtkit as K
from deck.motifs import core as C
X, Y = 390.0, 200.0
fc = JF.profile_left((X, Y))
f = K.outline(fc.head, K.FINE) + fc.lines
import numpy as np
print(fc.head[:600])
render([f], (X - 75, Y - 50, X + 55, Y + 100), "/home/luke/Projects/design/san-marcos-deck/work/jh/exp/dbg.png", 520)
