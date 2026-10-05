import sys, importlib
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/kc")
from snap import render, scene_of
from deck import courtkit as K
import art._kc_crown as CR
importlib.reload(CR)
variants = eval(sys.argv[1])
outs = []
for i, kw in enumerate(variants):
    fc = K.face((375.0, 207.0), "frontal", age="elder", lids="lowered")
    hs = K.HairSpec(top=(-52.0, -30.0), bulge=(-64.0, 40.0), bottom=(-53.0, 110.0), ribbons=4)
    parts = [(f"hair{s}", K.hair_fall(fc, s, hs)) for s in (-1, 1)]
    sc = K.Scene(rank="K")
    for n, p in parts: sc.part(n, p)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("crown", CR.knee_crown(**kw))
    o = f"/home/luke/Projects/design/san-marcos-deck/work/kc/t/crown{i}.png"
    render(sc.layers(), o, (285, 60, 180, 200), 3.0)
    outs.append(o)
import subprocess
subprocess.run(["magick", *outs, "+append", "/home/luke/Projects/design/san-marcos-deck/work/kc/t/crowns.png"], check=True)
