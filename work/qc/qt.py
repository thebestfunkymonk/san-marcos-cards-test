"""Quick region render: python work/qc/qt.py <fn> <out.png> x0 y0 x1 y1 scale [module]
Calls QC.<fn>() -> (Scene, face) , composes (heal), renders the region (no frame) at ``scale``×."""
import importlib.util, os, subprocess, sys, time
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
from deck import tokens as T
fn, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1, sc_ = map(float, sys.argv[3:8])
mod = sys.argv[8] if len(sys.argv) > 8 else ROOT + "/art/QC.py"
spec = importlib.util.spec_from_file_location("draft", mod)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
t = time.time()
res = getattr(m, fn)()
sc = res[0] if isinstance(res, tuple) else res
f = sc.compose()
print(f"compose {time.time()-t:.1f}s  heal entries {len(sc.heal_log)}")
for e in sc.heal_log:
    if e.get("action") == "UNRESOLVED" or e.get("role") in ("lid", "lid-lo", "pupil", "brow", "nose", "mouth", "lip"):
        print("   ", {k: e[k] for k in e if k != 'geom'})
parts = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>']
lay = f.layers()
for L in T.LAYERS:
    if lay.get(L):
        parts.append(lay[L])
W = int((x1 - x0) * sc_)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{W}" '
       f'height="{int(W*(y1-y0)/(x1-x0))}">' + "".join(parts) + "</svg>")
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(W), out.replace(".png", ".svg"), "-o", out], check=True)
