import sys, math; sys.path.insert(0,"build/review"); sys.path.insert(0,".")
from rend import out
from deck import tokens as T
from deck.motifs import fauna as FA, core as C
a=-60
x = 375 + 175*math.cos(math.radians(a)); y = 525 + 175*math.sin(math.radians(a))
dd = FA.fountain_darter(x, y, 100, rot=a+90)
out(dd, "ko-a", (400, 330, 520, 410), 4, flood=T.JADE)
out(dd.rot180(), "ko-b", (230, 640, 350, 720), 4, flood=T.JADE)
d0 = FA.fountain_darter(60, 40, 100)
out(d0, "ko-c", (0, 5, 120, 65), 4, flood=T.JADE)
d1 = FA.fountain_darter(60, 40, 100, rot=30)
out(d1, "ko-d", (0, -10, 120, 90), 4, flood=T.JADE)
