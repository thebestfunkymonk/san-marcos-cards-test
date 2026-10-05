"""Review scratch: Q index with native vertical tail vs a diagonal-tail mock (brief-level exception)."""
import subprocess, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from shapely.geometry import Polygon, box
from shapely import affinity
from deck import index as I, tokens as T
from inkkit import geom as G

q = G.to_shape(I.rank_d("Q"), tol=0.05)
x0, y0, x1, y1 = q.bounds
print("Q bbox", [round(v, 2) for v in q.bounds])
# measure the tail: part below the bowl's bottom (baseline + O overshoot ~1.1)
tail = q.intersection(box(0, 143.5, 200, 200))
print("tail bbox", [round(v, 2) for v in tail.bounds], "width", round(tail.bounds[2] - tail.bounds[0], 2))
# mock: remove the tail, add a diagonal tail of the same thickness from the bowl's lower right
tw = tail.bounds[2] - tail.bounds[0]
noq = q.difference(box(0, 141.0, 200, 200)).union(q.intersection(box(0, 0, 200, 141.0)))
bowl_bottom = G.to_shape(I.rank_d("O"), tol=0.05) if False else None
cx = (x0 + x1) / 2
# base the new tail on the stem direction ~ -55° (down-right), from inside the bowl wall
L = 30.0
import math
a = math.radians(50)
dx, dy = math.cos(a), math.sin(a)
nx, ny = -dy, dx
sx, sy = cx + 6, 131.0
pts = [(sx + nx * tw / 2, sy + ny * tw / 2), (sx - nx * tw / 2, sy - ny * tw / 2),
       (sx - nx * tw / 2 + dx * L, sy - ny * tw / 2 + dy * L), (sx + nx * tw / 2 + dx * L, sy + ny * tw / 2 + dy * L)]
diag = Polygon(pts)
# keep bowl counter clear: only add the tail outside the counter
counter = q.convex_hull.difference(q).buffer(0)
qd = q.difference(box(0, 142.6, 200, 200)).union(diag)
# clip the diagonal tail so it doesn't enter the counter
print("mock Q bbox", [round(v, 2) for v in qd.bounds])
pip = I.index_pip_d("C")
def card(qshape, label):
    return (f'<path d="{G.from_shape(qshape)}" fill="{T.INK}"/><path d="{pip}" fill="{T.INK}"/>')
W, H = 170, 250
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{2*W}" height="{H}" viewBox="0 0 {2*W} {H}">'
       f'<rect width="{2*W}" height="{H}" fill="{T.PAPER}"/>'
       f'<g transform="translate(0 0)">{card(q, "native")}</g>'
       f'<g transform="translate({W} 0)">{card(qd, "diag")}</g></svg>')
p = "/home/luke/Projects/design/san-marcos-deck/build/review/q_mock"
open(p + ".svg", "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(2 * W), p + ".svg", "-o", p + "_1x.png"], check=True)
subprocess.run(["rsvg-convert", "-w", str(int(2 * W * 0.25)), p + ".svg", "-o", p + "_25.png"], check=True)
