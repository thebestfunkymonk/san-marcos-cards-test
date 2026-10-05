"""Window bench: render art/_kh_window.window() alone (knockout geometry, no heal) at N×."""
import sys, subprocess, importlib
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import art._kh_window as KW
importlib.reload(KW)
from deck import tokens as T
from deck.motifs import core as C
out = sys.argv[1]
scale = float(sys.argv[2]) if len(sys.argv) > 2 else 5
kw = eval("dict(" + (sys.argv[3] if len(sys.argv) > 3 else "") + ")")
cx, cy = 375.0, 428.0
p = KW.window(cx, cy, **kw)
f = p.fills + p.lines
L = f.layers()
body = "".join(L.get(k, "") for k in ("paper", "jade", "red", "gold", "ink"))
x0, y0, w, h = cx - 80, cy - 60, 160, 120
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*scale:.0f}" height="{h*scale:.0f}">'
       f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{T.PAPER}"/>{body}</svg>')
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", out.replace(".png", ".svg"), "-o", out], check=True)
# 1x version too
svg1 = svg.replace(f'width="{w*scale:.0f}" height="{h*scale:.0f}"', f'width="{w:.0f}" height="{h:.0f}"')
open(out.replace(".png", "_1x.svg"), "w").write(svg1)
subprocess.run(["rsvg-convert", out.replace(".png", "_1x.svg"), "-o", out.replace(".png", "_1x.png")], check=True)
if "report" in sys.argv:
    field = [m for m in p.fills.marks if m.layer == "jade"]
    print(C.knockout_report(p.meta["inner_d"], "", ))
