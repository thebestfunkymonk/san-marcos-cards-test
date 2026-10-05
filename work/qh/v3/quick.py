"""Quick top-half render of art/QH.py: python work/qh/v3/quick.py out.png [scale] [x0 y0 x1 y1]"""
import os, subprocess, sys, time, importlib
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
from deck import tokens as T, frames as F
import art.QH as Q
t0 = time.time()
sc = Q.figure()
frag = sc.compose()
out = sys.argv[1]
scale = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
box = [float(v) for v in sys.argv[3:7]] if len(sys.argv) > 6 else [128, 44, 622, 540]
x0, y0, x1, y1 = box
L = frag.layers()
parts = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>']
for lay in T.LAYERS:
    if lay in L:
        parts.append(L[lay])
# frame + band line for reference
parts.append(f'<path d="{F.art_window_d()}" fill="none" stroke="#999" stroke-width="0.6"/>')
parts.append(f'<path d="{F.corner_pip_d("H")}" fill="{T.RED}"/>')
parts.append(f'<line x1="128" y1="511" x2="622" y2="511" stroke="{T.INK}" stroke-width="2.1"/>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{int((x1-x0)*scale)}" '
       f'height="{int((y1-y0)*scale)}">' + "".join(parts) + "</svg>")
sp = out.replace(".png", ".svg")
open(sp, "w").write(svg)
subprocess.run(["rsvg-convert", sp, "-o", out], check=True)
print(f"{time.time()-t0:.1f}s heal entries: {len(sc.heal_log)}")
for e in sc.heal_log[:60]:
    print("  ", e)
