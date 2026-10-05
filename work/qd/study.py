"""Render a subset of QD's scene (by part name prefix) in a crop at 3x — fast
iteration on one region. usage: study.py <out.png> x0 y0 x1 y1 [names,comma] [scale]"""
import os, subprocess, sys, time
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
from deck import courtkit as K, tokens as T
import QD
out = sys.argv[1]
x0, y0, x1, y1 = map(float, sys.argv[2:6])
names = sys.argv[6].split(",") if len(sys.argv) > 6 and sys.argv[6] != "all" else None
scale = float(sys.argv[7]) if len(sys.argv) > 7 else 3
t = time.time()
sc = QD.figure()
if names:
    sc.items = [it for it in sc.items if any(it.name.startswith(n) for n in names)]
f = sc.compose()
lay = f.layers()
parts = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>']
for L in T.LAYERS:
    if lay.get(L):
        parts.append(lay[L])
w = int((x1 - x0) * scale)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{w}" '
       f'height="{int(w*(y1-y0)/(x1-x0))}">' + "".join(parts) + "</svg>")
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(w), out.replace(".png", ".svg"), "-o", out], check=True)
print(out, "heal", len(sc.heal_log), "t=%.1f" % (time.time() - t))
for e in sc.heal_log:
    if isinstance(e, dict) and "UNRES" in str(e):
        print("  ", e)
