from rv import *
from deck.motifs import *
import math
ang=-60
x=375+175*math.cos(math.radians(ang)); y=525+175*math.sin(math.radians(ang))
d=fountain_darter(x,y,100,rot=ang+90)
pair = d + d.rot180()
save(d, "orbit_darter_1oclock_ko", zoom=4, flood=T.JADE, pad=12)
save(d, "orbit_darter_1oclock_line", zoom=4, pad=12)
