from rh import *
from deck.motifs import geometric as M
from inkkit import geom as G
from deck.motifs import forms as FM
row = C.Frag(); x = 20
for r in (40, 24, 16, 12, 10):
    try:
        f = M.rowel_star(x + r, 50, r)
        ts = FM.tight_spots(f, 4.2)
        print(f"rowel r_out {r}: marks {len(f)}, ground<4.2 {ts['area']:.0f}px2, warnings {f.meta.get('warnings')}")
        row += f
    except Exception as e:
        print("rowel", r, "FAILED", type(e).__name__, e)
    x += 2 * r + 20
show(row, "rowels-4x", zoom=4, view=(0, 0, x, 100))
for r in (12, 10):
    s = M.rowel_star(0, 0, r, solid=True)
    x0,y0,x1,y1 = s.bbox(); print(f"solid rowel r_out {r}: bbox {x1-x0:.1f}")
st = C.Frag(); x = 10
for L in (64, 48, 36, 28, 22):
    f = M.stalactite(x, 10, L, L * 20 / 64)
    st += f; x += L * 20 / 64 + 10
    print(f"stalactite L{L}: rings {sum(1 for m in f.marks if m.role=='ring')}, hatch lines {sum(len(G.flatten(m.d)) for m in f.marks if m.role=='hatch')}")
show(st, "stalactites-6x", zoom=6)
