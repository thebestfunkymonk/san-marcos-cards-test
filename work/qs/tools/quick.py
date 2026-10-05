"""Quick render of art/QS.py's figure (top half only, no frame) for iteration.

    .venv/bin/python work/qs/tools/quick.py OUT.png [scale] [x0 y0 x1 y1]
"""
import os, subprocess, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
import importlib
from deck import tokens as T

out = sys.argv[1]
scale = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
box = [float(v) for v in sys.argv[3:7]] if len(sys.argv) > 6 else [139, 55, 611, 525]
t = time.time()
QS = importlib.import_module("art.QS")
sc = QS.figure()
lay = sc.layers()
print(f"compose {time.time()-t:.1f}s; heal log {len(sc.heal_log)}; unresolved "
      f"{sum(1 for e in sc.heal_log if e['action']=='UNRESOLVED')}")
x0, y0, x1, y1 = box
w, h = x1 - x0, y1 - y0
body = "".join("".join(v) if isinstance(v, list) else v for k in T.LAYERS for v in [lay.get(k, "")])
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*scale}" height="{h*scale}">'
       f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{T.PAPER}"/>{body}</svg>')
tmp = out.replace(".png", ".svg")
open(tmp, "w").write(svg)
subprocess.run(["rsvg-convert", tmp, "-o", out], check=True)
if "--log" in sys.argv:
    for e in sc.heal_log:
        print(e)
