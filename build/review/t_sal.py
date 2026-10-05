from rv import *
from deck.motifs import *
s = blind_salamander(0,0)
print(s.bbox())
save(s, "sal_full", zoom=3, ground=T.RED)
x0,y0,x1,y1 = s.bbox()
