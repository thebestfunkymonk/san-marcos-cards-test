import sys, subprocess; sys.path.insert(0,".")
from deck.motifs import rice as R
f = R.rice_wreath_arc(0,0,150)
g = f.mirror_x(0)
def P(fr, col): return "".join(f'<path d="{m.d}" fill="{col if m.kind=="fill" else "none"}" stroke="{col if m.kind!="fill" else "none"}" stroke-width="{m.w}" stroke-linecap="round" opacity="0.7"/>' for m in fr.marks)
open("build/review/wsym.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-190 10 370 170"><rect x="-190" y="10" width="370" height="170" fill="#fff"/>'+P(f,"#d00")+P(g,"#00d")+'</svg>')
subprocess.run(["rsvg-convert","-z","2","build/review/wsym.svg","-o","build/review/wsym.png"])
