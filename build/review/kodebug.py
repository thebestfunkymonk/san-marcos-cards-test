import sys, math; sys.path.insert(0,".")
from deck.motifs import fauna as FA, core as C
from inkkit import geom as G
a=-60
x = 375 + 175*math.cos(math.radians(a)); y = 525 + 175*math.sin(math.radians(a))
for name, dd in (("orbit", FA.fountain_darter(x, y, 100, rot=a+90)), ("orbit180", FA.fountain_darter(x, y, 100, rot=a+90).rot180()), ("plain", FA.fountain_darter(60,40,100))):
    tot = G.to_shape(dd.outline(), tol=0.05).area
    print(name, "outline area", round(tot,1))
    for i,m in enumerate(dd.marks):
        s = G.to_shape(G.from_skia(m.skia()), tol=0.05)
        A = s.area
        if A > 150: print("   mark", i, m.kind, m.role, m.w, round(A,1), m.d[:60])
