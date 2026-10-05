from rv import *
from deck.motifs import *
from deck.motifs.forms import tight_spots
import numpy as np
s = blind_salamander(0,0)
save(s, "sal_head_zoom", view=(0,-110,100,-10), zoom=8, ground=T.RED)
save(s, "sal_tail_zoom", view=(-40,40,60,108), zoom=8, ground=T.RED)
ts = tight_spots(s)
print("tight area", ts["area"])
m = ts["mask"]; x0,y0,x1,y1 = ts["extent"]; res=ts["res"]
from scipy import ndimage
lab,n = ndimage.label(m)
sizes = ndimage.sum(m, lab, range(1,n+1))*res*res
order = np.argsort(-sizes)[:8]
for i in order:
    ys,xs = np.where(lab==i+1)
    print(round(sizes[i],1), "at", round(x0+xs.mean()*res,1), round(y0+ys.mean()*res,1))
