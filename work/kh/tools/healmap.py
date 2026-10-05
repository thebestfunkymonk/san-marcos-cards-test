"""Healed render of the top half with heal-log markers (red trim, blue delete, black UNRESOLVED)."""
import sys, subprocess, importlib
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import art.KH as KH
from deck import tokens as T
out = sys.argv[1]
S = 2.5
sc = KH.figure()
L = sc.layers()
body = "".join("".join(v) for v in L.values())
marks = ""
col = {"trim": "#ff00ff", "delete": "#0088ff", "UNRESOLVED": "#000000", "drop": "#ffaa00", "fill-hole": "#00cc00"}
for e in sc.heal_log:
    x, y = e["at"]
    marks += f'<circle cx="{x}" cy="{y}" r="3" fill="none" stroke="{col.get(e["action"], "#f00")}" stroke-width="1.2"/>'
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="139 55 472 460" width="{472*S:.0f}" height="{460*S:.0f}">'
       f'<rect x="0" y="0" width="750" height="1050" fill="{T.PAPER}"/>{body}{marks}</svg>')
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", out.replace(".png", ".svg"), "-o", out], check=True)
import collections
print(len(sc.heal_log), collections.Counter(e["action"] for e in sc.heal_log))
