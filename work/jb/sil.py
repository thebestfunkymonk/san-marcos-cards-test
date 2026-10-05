"""Silhouette drafting sheet: body+bill+tail solid, key points, limits."""
import sys, os, subprocess
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jb/src")
import importlib
import _joker_black_pose as P
from inkkit import geom as G
import shapely
out = sys.argv[1] if len(sys.argv) > 1 else "/home/luke/Projects/design/san-marcos-deck/work/jb/draft/sil"
sil = shapely.union_all([G.to_shape(P.body_d()), G.to_shape(P.bill_d()), G.to_shape(P.tail_outline_d())])
d = G.from_shape(sil)
els = [f'<rect width="750" height="1050" rx="37.5" fill="#F4EFE3"/>',
       f'<rect x="130" y="90" width="582" height="550" fill="none" stroke="#c88" stroke-width="1"/>',
       f'<rect x="37.5" y="310" width="92.5" height="330" fill="none" stroke="#c88" stroke-width="1"/>',
       f'<path d="{d}" fill="#15242B"/>']
pts = list(P.BODY_PTS)
for i, p in enumerate(pts):
    els.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2" fill="#e33"/>')
    els.append(f'<text x="{p[0]+4:.1f}" y="{p[1]-3:.1f}" font-size="9" fill="#e33">{i}</text>')
ex, ey = P.EYE_C
els.append(f'<circle cx="{ex}" cy="{ey}" r="{P.EYE_R}" fill="#B08D57"/>')
W = P.WING
tip = W(P.WING_LEN)
els.append(f'<line x1="{W.o[0]}" y1="{W.o[1]}" x2="{tip[0]}" y2="{tip[1]}" stroke="#1D5A55" stroke-width="2"/>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1050" width="750" height="1050">{"".join(els)}</svg>'
open(out + ".svg", "w").write(svg)
subprocess.run(["rsvg-convert", "-w", "750", out + ".svg", "-o", out + ".png"], check=True)
subprocess.run(["rsvg-convert", "-w", "188", out + ".svg", "-o", out + "-188.png"], check=True)
print(sil.bounds)
