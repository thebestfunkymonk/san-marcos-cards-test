import sys; sys.path.insert(0,".")
from deck.motifs import rice as R
import subprocess
PAL = {"leaf":"#c90","midrib":"#08c","hatch":"#e33"}
f = (R.ribbon_leaf(0, 60, -14, 170, bend=(12, -12)) + R.ribbon_leaf(0, 110, -8, 190, bend=(9, 9), hatch=-1) + R.ribbon_leaf(0, 150, 0, 150, bend=(0, 0)))
parts=[f'<path d="{m.d}" fill="none" stroke="{PAL.get(m.role,"#888")}" stroke-width="{m.w}" stroke-linecap="{m.cap}" stroke-linejoin="{m.join}" stroke-miterlimit="{m.miter}"/>' for m in f.marks]
open("build/review/leafroles.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 0 220 170"><rect x="-10" y="0" width="220" height="170" fill="#fff"/>'+"".join(parts)+'</svg>')
subprocess.run(["rsvg-convert","-z","4","build/review/leafroles.svg","-o","build/review/leafroles.png"])
