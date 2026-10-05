import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qs/tools")
from r import render, montage
from deck import courtkit as K
import importlib
import art._qs_parts as Q
c = (512.0, 362.0)
OUT = "/home/luke/Projects/design/san-marcos-deck/work/qs/p5/"
variants = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [{}]
files = []
for i, v in enumerate(variants):
    pts = v.pop("pts", [(-31, -28), (-22, -19), (-8, -5), (4, 8), (10, 17), (12, 27), (6, 35), (-3, 38)])
    k = v.pop("k", 1.0)
    dx, dy = v.pop("d", (0, 0))
    sal_pts = [(c[0] + x * k + dx, c[1] + y * k + dy) for x, y in pts]
    sc = K.Scene()
    m = Q.mirror(c, v.pop("rf", 42.0), v.pop("rr", 55.0), handle_to=508.0, sal_pts=sal_pts, **v)
    sc.part("m", m)
    lay = sc.layers()
    files.append(render(lay, OUT + f"mir{i}.png", (452, 300, 572, 425), 5))
    for e in sc.heal_log:
        print(i, e)
montage(files, OUT + "mirrors.png", tile=f"{len(files)}x1")
