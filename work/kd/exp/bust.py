"""Fast partial render for K♦ experiments.

usage: bust.py <module.py> <out.png> [x0 y0 w h] [scale] [--noheal]
The module must expose figure() -> Scene. Renders only the art layers
(no frame/band/clip/rotation) on Limestone, cropped to the given card-px box.
"""
import importlib.util
import os
import subprocess
import sys

ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
from deck import courtkit as K  # noqa
from deck import tokens as T  # noqa

args = [a for a in sys.argv[1:] if not a.startswith("--")]
noheal = "--noheal" in sys.argv
mod_path, out = args[0], args[1]
box = [float(v) for v in args[2:6]] if len(args) >= 6 else [139, 55, 472, 456]
scale = float(args[6]) if len(args) >= 7 else 3.0
spec = importlib.util.spec_from_file_location("bustmod", mod_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
sc = m.figure()
lay = K.layers(sc.compose(heal_gaps=not noheal))
x0, y0, w, h = box
parts = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{T.PAPER}"/>']
for L in T.LAYERS:
    v = lay.get(L)
    if not v:
        continue
    parts.append(f'<g id="{L}">' + ("".join(v) if isinstance(v, list) else v) + "</g>")
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*scale:.0f}" '
       f'height="{h*scale:.0f}">' + "".join(parts) + "</svg>")
tmp = out[:-4] + ".svg"
open(tmp, "w").write(svg)
subprocess.run(["rsvg-convert", tmp, "-o", out], check=True)
if not noheal and sc.heal_log:
    print(f"heal: {len(sc.heal_log)} entries")
    for e in sc.heal_log[:40]:
        print("  ", e)
