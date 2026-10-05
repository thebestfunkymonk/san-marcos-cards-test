"""diag.py x y r scale out.png : colour each ink stroke near (x,y) separately over the fills."""
import sys, subprocess
sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import Point
from art import KH
from deck import courtkit as K
from inkkit import geom as G
x, y, r, s = map(float, sys.argv[1:5]); out = sys.argv[5]
res = KH.figure().compose()
q = Point(x, y).buffer(r * 1.5)
cols = ['#e6194b','#3cb44b','#4363d8','#f58231','#911eb4','#42d4f4','#f032e6','#bfef45','#469990','#9A6324','#800000','#000075']
fillc = {'jade':'#1D5A55','red':'#AE2F2B','gold':'#B08D57','ink':'#15242B','paper':'#F4EFE3'}
body = []; k = 0; legend = []
for m in res.marks:
    if not m.d: continue
    if m.kind == 'fill':
        body.append(f'<path d="{m.d}" fill="{fillc.get(m.layer, "#888")}" fill-rule="evenodd"/>')
for m in res.marks:
    if not m.d or m.kind != 'stroke': continue
    g = K.R(G.from_skia(m.skia()))
    if g.intersects(q):
        c = cols[k % len(cols)]; k += 1
        legend.append(f'{c} {m.role} w={m.w}')
        body.append(f'<path d="{m.d}" fill="none" stroke="{c}" stroke-opacity="0.6" stroke-width="{m.w}" stroke-linecap="{m.cap}" stroke-linejoin="{m.join}"/>')
        for p, closed in G.flatten(m.d, 0.05):
            for e in (p[0], p[-1]):
                if abs(e[0]-x) < r and abs(e[1]-y) < r:
                    body.append(f'<circle cx="{e[0]}" cy="{e[1]}" r="{0.15}" fill="yellow"/>')
    elif m.kind == 'stroke':
        body.append(f'<path d="{m.d}" fill="none" stroke="#15242B" stroke-width="{m.w}" stroke-linecap="{m.cap}" stroke-linejoin="{m.join}"/>')
x0, y0 = x - r, y - r
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{2*r*s:.0f}" height="{2*r*s:.0f}" viewBox="{x0} {y0} {2*r} {2*r}"><rect x="{x0}" y="{y0}" width="{2*r}" height="{2*r}" fill="#F4EFE3"/>' + ''.join(body)
for gx in range(int(x0), int(x0 + 2*r) + 1):
    svg += f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y0+2*r}" stroke="#ff00ff" stroke-opacity="0.3" stroke-width="{0.6/s}"/>'
for gy in range(int(y0), int(y0 + 2*r) + 1):
    svg += f'<line x1="{x0}" y1="{gy}" x2="{x0+2*r}" y2="{gy}" stroke="#ff00ff" stroke-opacity="0.3" stroke-width="{0.6/s}"/>'
svg += '</svg>'
open(out + '.svg', 'w').write(svg)
subprocess.run(['rsvg-convert', out + '.svg', '-o', out], check=True)
print(out); print('\n'.join(legend))
