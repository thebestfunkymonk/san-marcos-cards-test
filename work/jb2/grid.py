import os, subprocess, sys
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "work/jb2/src"))
import shapely
from inkkit import geom as G
import _joker_black_pose as P
import _joker_black_plumage as PL
x0, y0, x1, y1 = [float(v) for v in sys.argv[1:5]]
SC = float(os.environ.get("SC", "3"))
extra = sys.argv[5] if len(sys.argv) > 5 else ""
A = PL.anatomy()
els = ['<rect x="0" y="0" width="750" height="1050" fill="#F4EFE3"/>', f'<path d="{G.from_shape(A["core"])}" fill="#9aa4a8"/>']
if "lines" in extra:
    inner = A["core"].buffer(-PL.INSET)
    lines = PL.visible_lines(A["stack"], inner)
    ko = shapely.union_all(lines).buffer(PL.KO / 2, quad_segs=8)
    els.append(f'<path d="{G.from_shape(ko.intersection(A["core"]))}" fill="#fff"/>')
for x in range(int(x0) // 10 * 10, int(x1) + 1, 10):
    c = "#c33" if x % 50 == 0 else "#e9a"
    els.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{c}" stroke-width="{0.35 if x%50 else 0.6}"/>')
    if x % 50 == 0: els.append(f'<text x="{x+0.8}" y="{y0+5}" font-size="4.5" fill="#c33">{x}</text>')
for y in range(int(y0) // 10 * 10, int(y1) + 1, 10):
    c = "#c33" if y % 50 == 0 else "#e9a"
    els.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{c}" stroke-width="{0.35 if y%50 else 0.6}"/>')
    if y % 50 == 0: els.append(f'<text x="{x0+1}" y="{y-0.8}" font-size="4.5" fill="#c33">{y}</text>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{(x1-x0)*SC}" height="{(y1-y0)*SC}">{"".join(els)}</svg>'
p = os.path.join(ROOT, "work/jb2/out/grid.svg"); open(p, "w").write(svg)
subprocess.run(["rsvg-convert", p, "-o", os.path.join(ROOT, "work/jb2/out/grid.png")], check=True)
