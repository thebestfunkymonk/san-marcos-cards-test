"""Debug overlay: silhouette + knockout centrelines by family, 3x crop."""
import sys, subprocess
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jb2/src")
import numpy as np, shapely
from shapely.geometry import LineString, Polygon
from inkkit import geom as G
import _joker_black_pose as P, _joker_black_plumage as PL, _joker_black_props as PR

sil = PL.silhouette(PR.legs())
wing = PL.wing_shape()
els = [f'<path d="{G.from_shape(sil)}" fill="#cfd3d6"/>',
       f'<path d="{G.from_shape(wing)}" fill="#b7c0c6"/>']
def pl(g, col, w=1.2):
    for l in PL.lines_of(g):
        c = np.asarray(l.coords)
        d = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in c)
        els.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}"/>')
wl, rows = PL.wing_lines()
pl(shapely.union_all(wl), "#d22")
tail = PL.tail_shape()
pl(shapely.union_all(PL.tail_lines(tail, None)), "#22d")
body = PL.body_shape()
edge_pts = PL.wing_edge_pts()
W = P.WING; L = PL.L
side = shapely.make_valid(Polygon(np.vstack([edge_pts, [W(L + 60.0, 200.0), W(-150.0, 200.0), W(-150.0, -54.0)]])))
neck_cut = Polygon([P.BODY(104, -300), P.BODY(104, 300), P.BODY(400, 300), P.BODY(400, -300)])
region = (body.buffer(-PL.EDGE).intersection(side).difference(neck_cut)
          .difference(LineString(edge_pts).buffer(PL.KO + 4.2))
          .difference(tail.difference(body).buffer(4.2)))
els.append(f'<path d="{G.from_shape(region)}" fill="#9d9" fill-opacity="0.5"/>')
pl(shapely.union_all(PL.breast_arcs(region)), "#080")
pl_ = PL.build(extra_solid=PR.legs())
els.append(f'<path d="{G.from_shape(pl_["windows"])}" fill="#fc6" fill-opacity="0.6"/>')
out = sys.argv[1]
x0, y0, w, h = [float(v) for v in sys.argv[2:6]]
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*3}" height="{h*3}"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#fff"/>{"".join(els)}</svg>'
open(out + ".svg", "w").write(svg)
subprocess.run(["rsvg-convert", out + ".svg", "-o", out + ".png"], check=True)
