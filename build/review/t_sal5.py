from rv import *
from deck.motifs import *
from deck.motifs.forms import tight_spots
s = blind_salamander(0,0,radius=34, rot=20)
x0,y0,x1,y1=s.bbox(); print("bbox size", x1-x0, y1-y0, "warnings", s.meta.get("warnings"))
print("tight", tight_spots(s)["area"])
save(s, "sal_r34_mirror_jade_ko", zoom=5, flood=T.JADE, pad=8)
save(s, "sal_r34_line", zoom=5, pad=8)
