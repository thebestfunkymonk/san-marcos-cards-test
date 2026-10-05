"""Plumage study render with jade + eye: .venv/bin/python work/jb2/plum2.py <tag>"""
import os, subprocess, sys
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "work/jb2/src"))
from inkkit import geom as G
from deck import tokens as T
import _joker_black_pose as P
import _joker_black_plumage as PL
OUT = os.path.join(ROOT, "work/jb2/out")
tag = sys.argv[1] if len(sys.argv) > 1 else "plum2"
R = PL.build()
f = R["jade"] + R["gold"] + R["ink"]
lay = f.layers()
els = ['<rect width="750" height="1050" fill="#F4EFE3"/>']
for L in ("jade", "gold"):
    if L in lay: els.append(lay[L])
els.append(f'<path d="{G.from_shape(R["solid"])}" fill="#15242B"/>')
if "ink" in lay: els.append(lay["ink"])
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
