"""Quick silhouette sketch of the pose (no plumage) beside the reference."""
import sys, os, subprocess
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jb2/src")
import importlib
import numpy as np
import shapely
from shapely.geometry import Polygon
from inkkit import geom as G
import _joker_black_pose as P

body = G.to_shape(P.body_d())
bill = G.to_shape(P.bill_d())
tail = Polygon(P.tail_outline_pts()).buffer(0)
sil = shapely.union_all([body, bill, tail])
els = [f'<path d="{G.from_shape(sil)}" fill="#15242B"/>']
# construction: wing axis, eye
w = [P.WING(0, 0), P.WING(P.WING_LEN, 0)]
els.append(f'<line x1="{w[0][0]}" y1="{w[0][1]}" x2="{w[1][0]}" y2="{w[1][1]}" stroke="#c33" stroke-width="1"/>')
ex, ey = P.EYE_C
els.append(f'<circle cx="{ex}" cy="{ey}" r="{P.EYE_R}" fill="#B08D57"/>')
for y in (90, 310, 640):
    els.append(f'<line x1="0" y1="{y}" x2="750" y2="{y}" stroke="#39f" stroke-width="1"/>')
els.append('<line x1="130" y1="0" x2="130" y2="310" stroke="#39f" stroke-width="1"/>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1050" width="750" height="1050"><rect width="750" height="1050" fill="#F4EFE3"/>{"".join(els)}</svg>'
out = sys.argv[1] if len(sys.argv) > 1 else "/home/luke/Projects/design/san-marcos-deck/work/jb2/sketch"
open(out + ".svg", "w").write(svg)
subprocess.run(["rsvg-convert", out + ".svg", "-o", out + ".png"], check=True)
b = sil.bounds
print("bounds", [round(v, 1) for v in b], "w", round(b[2]-b[0]), "h", round(b[3]-b[1]))
