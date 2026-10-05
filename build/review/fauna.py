import sys; sys.path.insert(0,"build/review"); sys.path.insert(0,".")
from rend import out
from deck import tokens as T
from deck.motifs import fauna as FA, core as C
d = FA.fountain_darter(60, 20, 100)
out(d, "darter100-6x", (5, 0, 115, 40), 6)
out(d, "darter100-ko-6x", (5, 0, 115, 40), 6, flood=T.JADE)
out(d, "darter100-1x", (0, 0, 120, 40), 1)
# back usage: C2 pair on orbit
import math
a = -60
x = 375 + 175*math.cos(math.radians(a)); y = 525 + 175*math.sin(math.radians(a))
dd = FA.fountain_darter(x, y, 100, rot=a+90)
out(dd + dd.rot180(), "darter-pair-ko", (150, 300, 600, 750), 2, flood=T.JADE)
print(dd.bbox())
d = FA.fountain_darter(60, 40, 100)
print(d.bbox())
out(d, "darter100b-6x", (5, 10, 115, 62), 6)
out(d, "darter100b-ko-6x", (5, 10, 115, 62), 6, flood=T.JADE)
out(d, "darter100b-1x", (0, 5, 120, 65), 1)
