"""Fast crop render of art/JH.figure() without the card system: python work/jh/v3/scene.py name x0 y0 x1 y1 width"""
import sys, time, subprocess, importlib
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
from deck import tokens as T
t0 = time.time()
import art.JH as JH
sc = JH.figure()
f = sc.compose()
print(f"compose {time.time()-t0:.1f}s; heal entries {len(sc.heal_log)}")
for e in sc.heal_log:
    print("  heal:", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in e.items() if k != 'd'})
name = sys.argv[1] if len(sys.argv) > 1 else "crop"
x0, y0, x1, y1 = map(float, sys.argv[2:6]) if len(sys.argv) > 5 else (139, 55, 611, 511)
w = int(sys.argv[6]) if len(sys.argv) > 6 else 1200
L = f.layers()
parts = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>']
for k in T.LAYERS:
    if L.get(k):
        parts.append(L[k])
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{w}" '
       f'height="{int(w*(y1-y0)/(x1-x0))}">' + "".join(parts) + "</svg>")
p = f"{ROOT}/work/jh/v3/out/{name}.svg"
open(p, "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(w), p, "-o", p[:-4] + ".png"], check=True)
print(p[:-4] + ".png")
