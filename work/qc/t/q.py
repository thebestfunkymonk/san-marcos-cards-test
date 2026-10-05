"""Quick region render of art/QC.py with optional global overrides.
python work/qc/t/q.py out.png x0 y0 x1 y1 scale ["python stmts run in the QC module namespace"] [fn]"""
import importlib.util, subprocess, sys, time
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
from deck import tokens as T
out = sys.argv[1]
x0, y0, x1, y1, s = map(float, sys.argv[2:7])
stmts = sys.argv[7] if len(sys.argv) > 7 else ""
fn = sys.argv[8] if len(sys.argv) > 8 else "figure"
spec = importlib.util.spec_from_file_location("QCdraft", ROOT + "/art/QC.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
if stmts:
    exec(stmts, m.__dict__)
t = time.time()
res = getattr(m, fn)()
sc = res[0] if isinstance(res, tuple) else res
f = sc.compose()
print(f"compose {time.time()-t:.1f}s  heal {len(sc.heal_log)}")
for e in sc.heal_log:
    if e["action"] == "UNRESOLVED": print("   UNRESOLVED", {k: e[k] for k in e if k != "geom"})
lay = f.layers()
W = int((x1 - x0) * s)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{W}" height="{int(W*(y1-y0)/(x1-x0))}">'
       f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>' + "".join(lay.get(L, "") for L in T.LAYERS) + "</svg>")
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(W), out.replace(".png", ".svg"), "-o", out], check=True)
