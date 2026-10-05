import sys; sys.path.insert(0,"build/review"); sys.path.insert(0,".")
from rend import out
from deck import tokens as T
from deck.motifs import lion as L, core as C
from deck import frames as F
f = C.Frag()
for i,s in enumerate((60,48,40,32,24)):
    f += L.lion_mark(40+i*72, 40, s)
out(f, "mark-line-1x", (0,0,380,80), 1)
out(f, "mark-line-4x", (0,0,380,80), 4)
g = C.Frag()
for i,s in enumerate((60,48,40,32,24)):
    g += L.lion_mark(40+i*72, 40, s, style="solid")
out(g, "mark-solid-4x", (0,0,380,80), 4, under=[(f"M0 0h380v80h-380z", T.RED)])
out(g, "mark-solid-1x", (0,0,380,80), 1, under=[(f"M0 0h380v80h-380z", T.RED)])
out(g, "mark-solid-paper-4x", (0,0,380,80), 4)
for i,s in enumerate((60,48,40,32,24)):
    print(s, L.lion_mark(0,0,s).meta)
