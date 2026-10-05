from rv import *
from deck.motifs import *
import numpy as np
d = fountain_darter(0, 0, 100)
for m in d.marks:
    if m.role in ("saddle","stitch","spine"):
        print(m.role, m.d.count("M"))
# jade knockout, 1x and 3x
save(d, "darter100_ko_1x", zoom=1, flood=T.JADE, pad=10)
save(d, "darter100_ko_3x", zoom=3, flood=T.JADE, pad=10)
# eye geometry
from deck.motifs import fauna
D=fauna.DARTER; er=D['eye']['r']; print("eye ring centreline r", er, "inner clear diameter", 2*er-T.FINE, "pupil", D['eye']['dot'])
# odd size: 60 px and 160 px, rotated 33 deg, facing -1
d2 = fountain_darter(0,0,60, facing=-1, rot=33)
print("60px warnings", d2.meta.get("warnings"))
save(d2, "darter60_rot", zoom=6)
d3 = fountain_darter(0,0,160, facing=1)
print("160 warnings", d3.meta.get("warnings"))
save(d3, "darter160", zoom=4)
