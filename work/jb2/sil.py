"""Silhouette study: render the draft pose's silhouette beside the reference.

    .venv/bin/python work/jb2/sil.py <tag> [--pts]
"""
import os
import subprocess
import sys
import importlib

ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "work/jb2/src"))

import shapely  # noqa
from inkkit import geom as G  # noqa
import _joker_black_pose as P  # noqa

OUT = os.path.join(ROOT, "work/jb2/out")
tag = sys.argv[1] if len(sys.argv) > 1 else "sil"
show_pts = "--pts" in sys.argv

parts = [P.body_d(), P.bill_d(), P.tail_d(), P.wing_proj_d()]
extra = getattr(P, "extra_sil", lambda: [])()
sil = G.union(*(parts + extra))
els = [f'<rect width="750" height="1050" fill="#F4EFE3"/>',
       f'<path d="{sil}" fill="#15242B"/>']
ex, ey = P.EYE_C
els.append(f'<circle cx="{ex}" cy="{ey}" r="{P.EYE_R}" fill="#B08D57"/>')
els.append(f'<circle cx="{ex}" cy="{ey}" r="{P.PUPIL_D/2}" fill="#15242B"/>')
# guides: band and wire level
els.append('<line x1="0" y1="90" x2="750" y2="90" stroke="#AE2F2B" stroke-width="0.8"/>')
els.append('<line x1="0" y1="640" x2="750" y2="640" stroke="#AE2F2B" stroke-width="0.8"/>')
if show_pts:
    for i, p in enumerate(P.BODY_PTS):
        els.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="1.6" fill="#AE2F2B"/>')
        els.append(f'<text x="{p[0]+3:.1f}" y="{p[1]-2:.1f}" font-size="7" fill="#AE2F2B">{i}</text>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1050" width="750" height="1050">{"".join(els)}</svg>'
p = os.path.join(OUT, f"{tag}.svg")
open(p, "w").write(svg)
subprocess.run(["rsvg-convert", "-w", "2250", p, "-o", os.path.join(OUT, f"{tag}-2250.png")], check=True)
subprocess.run(["rsvg-convert", "-w", "188", p, "-o", os.path.join(OUT, f"{tag}-188.png")], check=True)
# crop the figure at 3x: x 240..540, y 60..660 -> 900 x 1800 ; show at 1/2 -> 450 x 900
crop = os.path.join(OUT, f"{tag}-crop.png")
subprocess.run(["magick", os.path.join(OUT, f"{tag}-2250.png"), "-crop", "900x1800+660+180", "+repage",
                "-resize", "50%", crop], check=True)
ref = os.path.join(ROOT, "research/refs/jokers/grackle_Great_tailed_Grackle_2_jpg.jpg")
subprocess.run(["magick", crop, "(", ref, "-resize", "x900", ")",
                "(", os.path.join(OUT, f"{tag}-188.png"), "-scale", "200%", ")", "+append",
                os.path.join(OUT, f"{tag}-cmp.png")], check=True)
print(os.path.join(OUT, f"{tag}-cmp.png"))
