from rv import *
from deck.motifs import *
from deck import frames
from inkkit import geom as G
import numpy as np
from collections import Counter
# A-club: wild-rice spray knocked out of the club at MEDIUM (brief H.15)
club = frames.ace_pip_d('C'); print("club bbox", [round(v,1) for v in G.bbox(club)])
st = rice_stalk(375, 560, -90, 190, w=T.MEDIUM)
lf = ribbon_leaf(375, 590, -150, 150, w=T.MEDIUM) + ribbon_leaf(375, 590, -30, 150, w=T.MEDIUM, hatch=-1)
spray = st + lf
print("widths used", Counter((m.role, m.w) for m in spray.marks if m.kind=="stroke"))
ko = knockout(club, spray)
rep = knockout_report(club, ko, min_line=2.5, min_gap=3.0)
print({k: round(v,3) for k,v in rep.items()})
ko_f = reversed_out(club, spray, color=T.INK)
save(ko_f, "ace_club_rice_ko", view=G.bbox(club), zoom=2.5, pad=0)
# A-heart: small rosette + bubbles in MEDIUM knocked out of heart
heart = frames.ace_pip_d('H'); print("heart bbox", [round(v,1) for v in G.bbox(heart)])
ros = source_rosette(375, 540, 40, twist=False, w=T.MEDIUM)
col = bubble_beading((375, 494), (375, 400), 4.2, n=5, w=T.MEDIUM)
ko2 = knockout(heart, ros, col)
rep2 = knockout_report(heart, ko2, min_line=2.5, min_gap=3.0)
print("heart", {k: round(v,3) for k,v in rep2.items()}, "col sizes", [m.kind for m in col.marks])
save(reversed_out(heart, ros, col, color=T.RED), "ace_heart_ko", view=G.bbox(heart), zoom=2.5, pad=0)
