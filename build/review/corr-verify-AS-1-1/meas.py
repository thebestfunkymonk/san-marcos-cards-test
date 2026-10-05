import sys, shapely
sys.path.insert(0,'.')
from deck import frames as F, tokens as T
from deck.motifs.core import Frag
from inkkit import geom as G
from art import AS, _as_legend as L, _as_water as W
dy=AS.COMPOSITION_DY
spade=G.to_shape(G.translate(F.ace_pip_d("S"),0,dy))
print("spade bounds", [round(v,2) for v in spade.bounds])
leg=L.legend().translate(0,dy)
# group marks by role/kind
def sh(m): return G.to_shape(G.from_skia(m.skia()))
rows=[]
for m in leg.marks:
    s=sh(m); rows.append((m.role,m.kind,s))
    print(m.role,m.kind,m.w,[round(v,2) for v in s.bounds], "cx=%.2f"%((s.bounds[0]+s.bounds[2])/2))
# lines
types=[s for r,k,s in rows if r=='type']
ems=[s for r,k,s in rows if r=='em-rule']
print("n type",len(types),"n em",len(ems))
for i in range(len(types)-1):
    a,b=types[i],types[i+1]
    print(f"gap type{i}->type{i+1}: bbox gap {b.bounds[1]-a.bounds[3]:.2f}, min dist {a.distance(b):.2f}")
arc=types[-1]; l3=types[-2]
l3all=shapely.union_all([l3]+[ems[-1]])
print("arc to line3 incl em-rules min dist %.2f"%arc.distance(l3all))
# arc vertical gap at the centre
cx=375
col=shapely.box(cx-3,0,cx+3,1050)
print("arc ink near centre", [round(v,2) for v in arc.intersection(shapely.box(360,0,390,1050)).bounds])
# em-rule gaps
for i,(t,e) in enumerate(zip([types[1],types[2]],ems)):
    tb=t.bounds; parts=list(getattr(e,'geoms',[e]))
    parts.sort(key=lambda p:p.bounds[0])
    print(f"line{i+2} ink x {tb[0]:.2f}-{tb[2]:.2f}; em-rule L {parts[0].bounds[0]:.2f}-{parts[0].bounds[2]:.2f} gapL {tb[0]-parts[0].bounds[2]:.2f}; R {parts[1].bounds[0]:.2f}-{parts[1].bounds[2]:.2f} gapR {parts[1].bounds[0]-tb[2]:.2f}; em y {parts[0].bounds[1]:.2f}-{parts[0].bounds[3]:.2f} ink y {tb[1]:.2f}-{tb[3]:.2f} ink mid {(tb[1]+tb[3])/2:.2f}")
em=G.to_shape(G.from_skia(Frag.select(AS.emblem().translate(0,dy),lambda m:True).marks[0].skia()))
