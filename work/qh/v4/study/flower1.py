import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qh/v4/study")
from render import render
from deck import courtkit as K
from art import _qh_attr as A
out = "/home/luke/Projects/design/san-marcos-deck/work/qh/v4/study/out"
sc = K.Scene()
V = [dict(centre="scallop", notch=5.0, squash=0.78, tilt=-10.0, hatch_rel=0.0), dict(centre="scallop", notch=5.0, squash=0.78, tilt=-10.0, hatch_rel=0.0, hatch_side=-1),
     dict(centre="scallop", notch=5.0, squash=0.78, tilt=-10.0, r_petal=50.0, petal_w=40.0), dict(centre="scallop", notch=6.0, squash=0.72, tilt=-12.0, r_petal=50.0, petal_w=40.0, hatch_rel=0.0)]
for k, kw in enumerate(V):
    cx = 100 + 120 * k
    sc.part(f"stem{k}", A.stem((cx, 220), (cx, 102), w=21.0))
    for nm, pt in A.flower3((cx, 100), **{**dict(r_petal=46.0, petal_w=37.0, centre_r=12.5), **kw}):
        sc.part(f"f{k}{nm}", pt)
log = render(sc, f"{out}/flower1.png", box=(30, 40, 530, 200), scale=3.0, small=0.25, guides=False)
