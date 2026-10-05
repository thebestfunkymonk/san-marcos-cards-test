from rv import *
from deck.motifs import *
from shapely.geometry import box
# 1. meta not transformed by rigid moves
c = conduit("M100 300 L100 100", 14)
c2_ = c.translate(200, 0)
print("hull bounds original", c.meta["hull"].bounds, "after translate", c2_.meta["hull"].bounds)
rules = stroke("M0 200 L400 200", style="rule")
broken = conduit_break(rules, c2_)
from inkkit import geom as G
for m in broken.marks:
    print("rule pieces after break by TRANSLATED conduit:", [ (round(p[0][0],1), round(p[-1][0],1)) for p,cl in G.flatten(m.d,0.1)])
save(rules.recolor(T.INK) , "dummy", zoom=1)
save(broken + c2_, "conduit_break_translated", view=(0,90,400,310), zoom=2)
# 2. warnings lost on +
a = fault_step(0,100,0,double=5)
b = ripple_rings(0,0,60,30,ratio=1,ry_ratio=8/60,mode="similar")
print("a warns", a.meta.get("warnings")); print("b warns", b.meta.get("warnings")); print("a+b warns", (a+b).meta.get("warnings"))
f = Frag(); f += a; f += b; print("+= warns", f.meta.get("warnings"))
print("c2(a) warns", c2(a).meta.get("warnings"))
