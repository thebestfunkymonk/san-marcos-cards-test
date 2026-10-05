from rh import *
from deck.motifs import lion as LI
a = LI.lion_andante(0, 0, clip_lens=True)
b = LI.lion_andante(0, 0, clip_lens=False)
from deck.motifs import geometric as M
geo = M.lens_geometry(0, -220, 220, 330)
lens = C.stroke(geo["d"], T.FINE, color=T.RED)
show(a + lens, "andante-tuft-clip-6x", zoom=6, ground=T.BOARD, view=(70,-180,135,-110))
show(b + lens, "andante-tuft-noclip-6x", zoom=6, ground=T.BOARD, view=(70,-180,135,-110))
show(a + lens, "andante-nose-clip-8x", zoom=8, ground=T.BOARD, view=(-165,-90,-120,-30))
