"""Head bench: python hb.py OUT.png 'python overrides on module KH (e.g. KH.BEARD=...)' [--heal] [x0 y0 w h scale]
Composes art/KH.figure() (optionally healed) and renders a crop."""
import sys, subprocess, importlib
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import art._kh_parts, art._kh_head, art._kh_window, art.KH as KH
from deck import courtkit as K
import art._kh_head as KHH, art._kh_parts as KP, art._kh_window as KW
from deck import tokens as T
out = sys.argv[1]
code = sys.argv[2] if len(sys.argv) > 2 else ""
heal = "--heal" in sys.argv
rest = [a for a in sys.argv[3:] if a != "--heal"]
x0, y0, w, h, scale = [float(v) for v in rest] if rest else (295.0, 120.0, 160.0, 220.0, 4.0)
if code:
    exec(code)
sc = KH.figure()
L = sc.layers(heal_gaps=heal)
body = "".join("".join(v) if isinstance(v, list) else v for k, v in L.items())
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*scale:.0f}" height="{h*scale:.0f}">'
       f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{T.PAPER}"/>{body}</svg>')
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", out.replace(".png", ".svg"), "-o", out], check=True)
if heal:
    import collections
    print(len(sc.heal_log), collections.Counter(e["action"] for e in sc.heal_log))
    for e in sc.heal_log:
        x, y = e["at"]
        if x0 <= x <= x0 + w and y0 <= y <= y0 + h:
            print(e)
