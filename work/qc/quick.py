"""Quick region render of a draft figure: python work/qc/quick.py <module> <out.png> x0 y0 x1 y1 width
Composes the scene (with heal) and renders only the top half region (no system frame)."""
import importlib.util, os, subprocess, sys, time
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
from deck import tokens as T
mod_path, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1, width = map(float, sys.argv[3:8])
spec = importlib.util.spec_from_file_location("draft", mod_path)
m = importlib.util.module_from_spec(spec); sys.path.insert(0, os.path.dirname(mod_path)); spec.loader.exec_module(m)
t = time.time()
sc, fc = m.figure()
f = sc.compose()
print(f"compose {time.time()-t:.1f}s  face strokes {fc.strokes}  heal entries {len(sc.heal_log)}")
for e in sc.heal_log:
    if e["action"] == "UNRESOLVED" or e["role"] in ("lid", "lid-lo", "pupil", "brow", "nose", "mouth", "lip", "spikelet", "awn", "floret"):
        print("   ", e)
parts = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>']
lay = f.layers()
for L in T.LAYERS:
    if lay.get(L):
        parts.append(lay[L])
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{int(width)}" '
       f'height="{int(width*(y1-y0)/(x1-x0))}">' + "".join(parts) + "</svg>")
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(int(width)), out.replace(".png", ".svg"), "-o", out], check=True)
