from rh import *
from deck.motifs import lion as LI
from inkkit import geom as G
row = C.Frag(); x = 40
for s in (60, 48, 40, 32, 24):
    row += LI.lion_mark(x, 40, s); x += s + 20
show(row, "mark-line-row-1x", zoom=1, view=(0,0,x,80))
show(row, "mark-line-row-6x", zoom=6, view=(0,0,x,80))
rs = C.Frag(); x = 40
for s in (60, 48, 40, 32, 24):
    rs += LI.lion_mark(x, 40, s, style="solid"); x += s + 20
show(rs, "mark-solid-row-6x", zoom=6, view=(0,0,x,80), ground=T.RED)
for s in (60, 40, 24):
    m = LI.lion_mark(0,0,s)
    print(s, "strokes(meta)", m.meta['strokes'], "detail", m.meta['detail'], "marks", len(m.marks), "subpaths", sum(len(G.flatten(mm.d)) for mm in m.marks if mm.kind=='stroke'))
