import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qh/v4/study")
from render import render
from deck import courtkit as K
from art import _qh_hand as HD
import importlib; importlib.reload(HD)
out = "/home/luke/Projects/design/san-marcos-deck/work/qh/v4/study/out"
sc = K.Scene()
bg = K.R(K.box(200, 380, 560, 520))
sc.add("bg", K.fill(bg, K.RED), bg, sil=True)
V = [dict(width=30.0, tips=(4.0, 0.0, 3.0, 9.0)), dict(width=30.0, tips=(5.0, 0.0, 3.0, 10.0), thumb=(0.10, 0.52), thumb_out=4.0, knuckle=0.45),
     dict(width=31.0, length=66.0, tips=(5.0, 0.0, 3.0, 10.0), thumb=(0.12, 0.5), thumb_out=5.0, knuckle=0.45, vgap=3.6)]
for k, kw in enumerate(V):
    HD.lady_hand((230.0 + 110 * k, 470.0), -24.0, **{**dict(length=62.0, width=29.0, wrist_w=25.0, side=-1), **kw}).add_to(sc, f"h{k}", halo=K.HALO)
log = render(sc, f"{out}/hand1.png", box=(200, 380, 560, 520), scale=4.0, guides=False)
for e in log: print(e)
