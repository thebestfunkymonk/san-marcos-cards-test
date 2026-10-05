import sys, subprocess
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/kc")
from snap import render
from deck import courtkit as K
import art._kc_regalia as RG
variants = eval(sys.argv[1])
outs = []
for i, v in enumerate(variants):
    sc = K.Scene(rank="K")
    c, r = (300.0, 414.0), 35.0
    sc.part("orb", getattr(RG, v.pop("fn", "cone_orb2"))(c, r, **v))
    K.cup(c, r, side=+1, wrist=(268.0, 482.0), wrist_w=26.0).add_to(sc, "hand", halo=0.0)
    o = f"/home/luke/Projects/design/san-marcos-deck/work/kc/t/orb{i}.png"
    render(sc.layers(), o, (250, 360, 110, 130), 3.0)
    outs.append(o)
subprocess.run(["magick", *outs, "+append", "/home/luke/Projects/design/san-marcos-deck/work/kc/t/orbs.png"], check=True)
