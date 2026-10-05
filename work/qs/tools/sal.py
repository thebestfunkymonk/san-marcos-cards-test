import os, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from deck import tokens as T, courtkit as K
from deck.motifs import core as C
import importlib
Q = importlib.import_module("art._qs_parts")
c = (510.0, 352.0)
pts = eval(sys.argv[2]) if len(sys.argv) > 2 else [(-26, -30), (-17, -21), (-8, -8), (1, 6), (7, 19), (6, 31), (-4, 38), (-16, 37)]
kw = eval(sys.argv[3]) if len(sys.argv) > 3 else {}
m = Q.mirror(c, kw.pop("rf", 47.0), kw.pop("rr", 58.0), handle_to=508.0, sal_pts=[(c[0]+x, c[1]+y) for x, y in pts], **kw)
f = m.fills + m.lines + K.outline(m.shape, K.CONTOUR)
lay = f.layers()
x0, y0, w, h = 440, 282, 140, 150
body = "".join(lay.get(k, "") for k in T.LAYERS)
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*6}" height="{h*6}"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{T.PAPER}"/>{body}</svg>'
out = sys.argv[1]
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", out.replace(".png", ".svg"), "-o", out], check=True)
