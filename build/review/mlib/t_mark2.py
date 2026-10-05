from rh import *
from deck.motifs import lion as LI
from deck.motifs import forms as FM
D = LI._MARK
for s in (60, 48, 40, 32, 24):
    k = (s - T.FINE) / (D["width"] - T.FINE)
    rf = D["face_r"] * k; pk = D["mane_peak"] * k
    clear = pk - T.FINE
    # angular scallop chord
    import math
    chord = 2 * math.pi * rf / 12
    m = LI.lion_mark(0, 0, s)
    ts = FM.tight_spots(m, 4.2)
    x0,y0,x1,y1 = m.bbox()
    print(f"{s}px: face r {rf:.2f}, mane peak offset {pk:.2f} -> scallop-to-face clear at peak {clear:.2f}px; scallop chord {chord:.2f}px; ground<4.2 area {ts['area']:.0f}px2 of bbox {(x1-x0)*(y1-y0):.0f}")
