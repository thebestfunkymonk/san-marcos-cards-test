"""Head-only iteration: python work/qc/headtest.py out.png  (renders head, hair, coronet, neck, gown top at 3x)."""
import os, subprocess, sys, time
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")
import importlib
from deck import tokens as T, courtkit as K
import QC
sc = K.Scene()
fc = QC.head_group(sc)
t = time.time(); f = sc.compose(); print(f"compose {time.time()-t:.1f}s strokes {fc.strokes}")
for e in sc.heal_log:
    print("   ", e)
x0, y0, x1, y1 = 290, 80, 490, 330
parts = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>']
lay = f.layers()
parts += [lay[L] for L in T.LAYERS if lay.get(L)]
W = 600
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{W}" height="{int(W*(y1-y0)/(x1-x0))}">' + "".join(parts) + "</svg>"
out = sys.argv[1]
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(W), out.replace(".png", ".svg"), "-o", out], check=True)
