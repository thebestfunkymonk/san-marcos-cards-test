from rv import *
from deck.motifs import *
from deck import frames
from inkkit import geom as G
from collections import Counter
dia = frames.ace_pip_d('D'); b=G.bbox(dia); print("diamond bbox", [round(v,1) for v in b])
# compass: N/S/E/W to within 18 px of tips; diagonals 60 %
r_out = (b[3]-b[1])/2 - 18
rose = rowel_star(375, 470, r_out, lengths=(1, .6), w=T.MEDIUM)
print(Counter((m.role, m.w) for m in rose.marks if m.kind=="stroke"))
ko = knockout(dia, rose)
rep = knockout_report(dia, ko, min_line=2.5, min_gap=3.0)
print({k: round(float(v),3) for k,v in rep.items()})
save(reversed_out(dia, rose, color=T.RED), "ace_dia_compass_ko", view=b, zoom=2, pad=0)
save(reversed_out(dia, rose, color=T.RED), "ace_dia_compass_ko_zoom", view=(375,380,440,470), zoom=8, pad=0)
# leaf at MEDIUM
lf = ribbon_leaf(0,0,0,160, w=T.MEDIUM)
print("leaf MEDIUM", Counter((m.role, m.w) for m in lf.marks if m.kind=="stroke"), lf.meta.get("width"))
