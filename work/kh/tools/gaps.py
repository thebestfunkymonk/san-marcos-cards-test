"""Near-miss finder (heal's §I.12 measure) on the UNHEALED composition: prints and draws each conflict."""
import sys, subprocess
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import numpy as np, shapely
from shapely.ops import nearest_points
import art.KH as KH
from deck import courtkit as K, tokens as T
from inkkit import geom as G
out = sys.argv[1]
region = [float(v) for v in sys.argv[2:6]] if len(sys.argv) > 5 else [139, 55, 472, 460]
sc = KH.figure()
f = sc.compose(heal_gaps=False)
band = K.C.stroke("M100 511L650 511", K.FINE, style="rule", role="_band")
f = f + band
marks = list(f.marks)
outl = {i: K.R(G.from_skia(m.skia())) for i, m in enumerate(marks) if m.d}
pieces = []
for grp in K._groups(marks):
    u = shapely.union_all([outl[i] for i in grp if i in outl])
    for pg in K._polys_of(u):
        if pg.area <= 0.05:
            continue
        mem = [i for i in grp if outl[i].intersects(pg)]
        m0 = marks[grp[0]]
        roles = sorted({(marks[i].role or marks[i].kind).split("@")[0] for i in mem})
        pieces.append((pg, m0.kind, m0.layer, roles))
geoms = [p[0] for p in pieces]
tree = shapely.STRtree(geoms)
A, B = tree.query(geoms, predicate="dwithin", distance=K.GAP)
bad = []
for a, b in zip(A, B):
    if a >= b:
        continue
    pa, pb = pieces[a], pieces[b]
    d = pa[0].distance(pb[0])
    if d < 0.08:
        continue
    both_fill = pa[1] == "fill" and pb[1] == "fill" and pa[2] == pb[2]
    need = K.GAP_FILL if both_fill else K.GAP_MARK
    if pa[1] == "stroke" and pb[1] == "stroke" and d >= K.GAP_MARK - 0.08:
        if K._run_len(pa[0], pb[0]) >= K.PAR_RUN - 0.5:
            need = K.GAP
        else:
            continue
    if d >= need - 0.08:
        continue
    p, q = nearest_points(pa[0], pb[0])
    bad.append((p, q, d, need, f"{pa[2]}:{'/'.join(pa[3])}", f"{pb[2]}:{'/'.join(pb[3])}"))
bad.sort(key=lambda t: (t[0].y, t[0].x))
x0, y0, w, h = region
for p, q, d, need, ra, rb in bad:
    if x0 <= p.x <= x0 + w and y0 <= p.y <= y0 + h:
        print(f"({p.x:6.1f},{p.y:6.1f}) {d:4.2f}<{need}  {ra}  <->  {rb}")
print(len(bad), "conflicts")
S = 3.0
L = f.select(lambda m: m.role != "_band").layers()
body = "".join(v for v in L.values())
mk = "".join(f'<line x1="{p.x}" y1="{p.y}" x2="{q.x}" y2="{q.y}" stroke="#ff00ff" stroke-width="1.5"/>'
             f'<circle cx="{p.x}" cy="{p.y}" r="4" fill="none" stroke="#ff00ff" stroke-width="0.8"/>' for p, q, *_ in bad)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*S:.0f}" height="{h*S:.0f}">'
       f'<rect x="0" y="0" width="750" height="1050" fill="{T.PAPER}"/>{body}{mk}</svg>')
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", out.replace(".png", ".svg"), "-o", out], check=True)
