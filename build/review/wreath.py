import sys; sys.path.insert(0,"build/review"); sys.path.insert(0,".")
from rend import out
from deck import tokens as T
from deck.motifs import rice as R
w = R.rice_wreath_arc(0, 0, 150)
print(w.bbox())
out(w, "wreath-knot-6x", (-40, 130, 40, 175), 6)
out(w, "wreath-tip-4x", (60, 60, 150, 150), 4)
out(w, "wreath-2x", (-160, 20, 160, 180), 2)
