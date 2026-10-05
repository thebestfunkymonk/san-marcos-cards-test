import sys, importlib
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qs/tools")
from r import render, montage
from deck import courtkit as K
import art._qs_parts as Q
OUT = "/home/luke/Projects/design/san-marcos-deck/work/qs/p5/"
root = (340.0, 300.0)
fan = [((-168.0, 130.0, -8.0)), ((-145.0, 128.0, -10.0)), ((-122.0, 110.0, -10.0))]
import math
variants = {
  "A": dict(n=6, barb_len=(20, 8), barb_w=(8, 5.5), angle=45),
  "B": dict(n=7, barb_len=(16, 6), barb_w=(6.6, 5.0), angle=38, spine_w=(9, 4)),
  "C": dict(n=6, barb_len=(22, 9), barb_w=(9, 6), angle=55, spine_w=(12, 5), spine_ko=0.7),
  "D": dict(n=6, barb_len=(14, 6), barb_w=(7, 5), angle=40, both=True, spine_w=(10, 4.4)),
}
files = []
for key, v in variants.items():
    sc = K.Scene()
    for i, (hd, L, sg) in enumerate(fan):
        tip = (root[0] + L * math.cos(math.radians(hd)), root[1] + L * math.sin(math.radians(hd)))
        p = Q.gill_frond((root[0] - 8 * i, root[1] + 10 * i), tip, sag=sg, side=+1, **v)
        sc.part(f"p{i}", p)
    lay = sc.layers()
    files.append(render(lay, OUT + f"plume{key}.png", (180, 150, 360, 330), 2.5))
montage(files, OUT + "plumes.png", tile="4x1")
