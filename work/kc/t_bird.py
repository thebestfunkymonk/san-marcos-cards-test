import sys, subprocess
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/kc")
from snap import render
from deck import courtkit as K
import art._kc_bird as BD, art._kc_regalia as RG
variants = eval(sys.argv[1])
outs = []
for i, v in enumerate(variants):
    sc = K.Scene(rank="K")
    sc.part("staff", RG.staff(x=540.0, top=187.0, hw=14.0, flute_kind="lines"))
    sc.part("finial", getattr(BD, v.pop("fn", "kingfisher"))((540.0, 176.0), **v))
    o = f"/home/luke/Projects/design/san-marcos-deck/work/kc/t/bird{i}.png"
    render(sc.layers(), o, (465, 65, 130, 150), 3.0)
    outs.append(o)
subprocess.run(["magick", *outs, "+append", "/home/luke/Projects/design/san-marcos-deck/work/kc/t/birds.png"], check=True)
