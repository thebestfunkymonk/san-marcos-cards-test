from rv import *
from deck.motifs import *
from deck.motifs.forms import tight_spots
for sz in (60, 40, 32):
    for st in ("line","solid"):
        m = lion_mark(0,0,sz, style=st)
        x0,y0,x1,y1 = m.bbox()
        ts = tight_spots(m)
        print(sz, st, "w", round(x1-x0,1), "h", round(y1-y0,1), "strokes", m.meta.get("strokes"), "detail", m.meta.get("detail"), "tight px2", ts["area"])
        g = T.RED if st=="solid" else T.PAPER
        save(m, f"mark{sz}_{st}", zoom=10, ground=g, pad=4)
# mane scallop chord at 40
import math
D=__import__("deck.motifs.lion", fromlist=["_MARK"])._MARK
k=(40-2.1)/(D["width"]-2.1); rf=D["face_r"]*k
print("40px: face r", round(rf,2), "mane peak r", round(rf+D["mane_peak"]*k,2), "scallop chord", round(2*math.pi*rf/12,2))
