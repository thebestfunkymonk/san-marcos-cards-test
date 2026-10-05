import sys; sys.path.insert(0,".")
from deck.motifs import rice as R
import subprocess
PAL = {"leaf":"#c90","midrib":"#08c","hatch":"#e33","stem":"#0a0","knot":"#a0a","knot-tail":"#a0a","spikelet":"#e33","stalk":"#08c","pedicel":"#08c","awn":"#e33"}
f = R.rice_wreath_arc(0, 0, 150)
from collections import Counter
print(Counter(m.role for m in f.marks))
for m in f.marks:
    if m.role=="stem": print("stem d len", len(m.d), m.d[:200])
parts=[f'<path d="{m.d}" fill="{PAL.get(m.role,"#888") if m.kind=="fill" else "none"}" stroke="{PAL.get(m.role,"#888") if m.kind!="fill" else "none"}" stroke-width="{m.w}" stroke-linecap="{m.cap}" stroke-linejoin="{m.join}"/>' for m in f.marks]
open("build/review/wreathroles.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-190 10 370 170"><rect x="-190" y="10" width="370" height="170" fill="#fff"/>'+"".join(parts)+'</svg>')
subprocess.run(["rsvg-convert","-z","2","build/review/wreathroles.svg","-o","build/review/wreathroles.png"])
b = f.bbox(); print(b)
