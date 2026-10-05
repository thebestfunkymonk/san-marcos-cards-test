"""Head bench: compose art/KH.figure() (optionally a subset) and render a crop at N×, no heal unless --heal."""
import sys, subprocess, importlib
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import art._kh_parts, art._kh_head, art._kh_window, art.KH as KH
for m in (art._kh_parts, art._kh_head, art._kh_window):
    importlib.reload(m)
importlib.reload(KH)
from deck import tokens as T
out = sys.argv[1]
x0, y0, w, h = [float(v) for v in sys.argv[2:6]]
scale = float(sys.argv[6]) if len(sys.argv) > 6 else 4
heal = "--heal" in sys.argv
sc = KH.figure()
L = sc.layers(heal_gaps=heal)
body = "".join("".join(v) for k, v in L.items())
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*scale:.0f}" height="{h*scale:.0f}">'
       f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{T.PAPER}"/>{body}</svg>')
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", out.replace(".png", ".svg"), "-o", out], check=True)
if heal:
    for e in sc.heal_log:
        print(e)
