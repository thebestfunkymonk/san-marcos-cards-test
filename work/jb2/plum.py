"""Plumage study render: .venv/bin/python work/jb2/plum.py <tag>"""
import os, subprocess, sys
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "work/jb2/src"))
import shapely
from inkkit import geom as G
import _joker_black_pose as P
import _joker_black_plumage as PL

OUT = os.path.join(ROOT, "work/jb2/out")
tag = sys.argv[1] if len(sys.argv) > 1 else "plum"
A = PL.anatomy()
inner = A["core"].buffer(-PL.INSET)
lines = PL.visible_lines(A["stack"], inner)
ko = shapely.union_all(lines).buffer(PL.KO / 2, quad_segs=8)
solid = A["core"].difference(ko)
els = ['<rect width="750" height="1050" fill="#F4EFE3"/>', f'<path d="{G.from_shape(solid)}" fill="#15242B" fill-rule="evenodd"/>']
ex, ey = P.EYE_C
els.append(f'<circle cx="{ex}" cy="{ey}" r="{P.EYE_R}" fill="#B08D57"/>')
els.append(f'<circle cx="{ex}" cy="{ey}" r="{P.PUPIL_D/2}" fill="#15242B"/>')
for y in (90, 640):
    els.append(f'<line x1="0" y1="{y}" x2="750" y2="{y}" stroke="#AE2F2B" stroke-width="0.8"/>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1050" width="750" height="1050">{"".join(els)}</svg>'
p = os.path.join(OUT, f"{tag}.svg"); open(p, "w").write(svg)
subprocess.run(["rsvg-convert", "-w", "2250", p, "-o", os.path.join(OUT, f"{tag}-2250.png")], check=True)
subprocess.run(["rsvg-convert", "-w", "188", p, "-o", os.path.join(OUT, f"{tag}-188.png")], check=True)
crop = os.path.join(OUT, f"{tag}-crop.png")
subprocess.run(["magick", os.path.join(OUT, f"{tag}-2250.png"), "-crop", "900x1800+660+180", "+repage", "-resize", "50%", crop], check=True)
subprocess.run(["magick", crop, "(", os.path.join(OUT, f"{tag}-188.png"), "-crop", "100x160+50+18", "+repage", "-scale", "300%", ")", "+append", os.path.join(OUT, f"{tag}-cmp.png")], check=True)
print(os.path.join(OUT, f"{tag}-cmp.png"))
