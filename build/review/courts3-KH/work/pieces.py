"""pieces.py x y r scale out: heal's pre-heal pieces near (x,y), outlined in colours (fills: dashed)."""
import sys, subprocess
sys.path.insert(0, '.')
import shapely
from shapely.geometry import Point
from art import KH
from deck import courtkit as K
import deck.courtkit as KK
from inkkit import geom as G
x, y, r, s = map(float, sys.argv[1:5]); out = sys.argv[5]
cap = {}
orig = KK.heal
def h2(f, **kw):
    cap['f'] = f
    return orig(f, **kw)
KK.heal = h2
sc = KH.figure(); res = sc.compose()
f = cap['f']; marks = list(f.marks)
q = Point(x, y).buffer(r * 1.5)
outl = {i: K.R(G.from_skia(m.skia())) for i, m in enumerate(marks) if m.d and K.R(G.from_skia(m.skia())).intersects(q)}
cols = ['#e6194b','#3cb44b','#4363d8','#f58231','#911eb4','#42d4f4','#f032e6','#bfef45','#469990','#9A6324','#800000','#000075']
fillc = {'jade':'#1D5A55','red':'#AE2F2B','gold':'#B08D57','ink':'#15242B','paper':'#F4EFE3'}
body = []
# final render as backdrop
for m in res.marks:
    if not m.d: continue
    if m.kind == 'fill':
        body.append(f'<path d="{m.d}" fill="{fillc.get(m.layer)}" fill-rule="evenodd" opacity="0.5"/>')
    else:
        body.append(f'<path d="{m.d}" fill="none" stroke="#15242B" stroke-opacity="0.5" stroke-width="{m.w}" stroke-linecap="{m.cap}" stroke-linejoin="{m.join}"/>')
k = 0; leg = []
for grp in KK._groups(marks):
    u = [outl[i] for i in grp if i in outl]
    if not u: continue
    u = shapely.union_all(u)
    for pg in KK._polys_of(u):
        if not pg.intersects(q) or pg.area < 0.05: continue
        c = cols[k % len(cols)]; k += 1
        m0 = marks[grp[0]]
        leg.append(f"{c} {m0.kind} {m0.layer} {sorted({marks[i].role for i in grp if i in outl and outl[i].intersects(pg)})} area={pg.area:.1f}")
        body.append(f'<path d="{K.D(pg)}" fill="none" stroke="{c}" stroke-width="{2.0/s}" {"stroke-dasharray=\"%f %f\"" % (6/s, 3/s) if m0.kind=="fill" else ""}/>')
x0, y0 = x - r, y - r
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{2*r*s:.0f}" height="{2*r*s:.0f}" viewBox="{x0} {y0} {2*r} {2*r}"><rect x="{x0}" y="{y0}" width="{2*r}" height="{2*r}" fill="#fff"/>' + ''.join(body) + '</svg>'
open(out + '.svg', 'w').write(svg)
subprocess.run(['rsvg-convert', out + '.svg', '-o', out], check=True)
print(out); print('\n'.join(leg))
