from rh import *
from deck.motifs import lion as LI
from inkkit import geom as G
f = LI.lion_andante(0, 0)
# short pieces (<= 8px) of any stroke
for m in f.marks:
    if m.kind != "stroke": continue
    for p, cl in G.flatten(m.d, 0.05):
        L = G.Curve(p).length
        if L < 8 and m.role not in ("hatch","toe"):
            print("short piece", m.role, round(L,2), p[0].round(1))
# hatch lines whose ends are not on another stroke centreline
hatch = [p for m in f.marks if m.role=="hatch" for p,_ in G.flatten(m.d)]
others = C.Frag([m for m in f.marks if m.role!="hatch" and m.kind=="stroke"])
from shapely.geometry import Point, LineString, MultiLineString
cl = MultiLineString([LineString(p) for m in others.marks for p,_ in G.flatten(m.d, 0.05) if len(p)>1])
free = []
for p in hatch:
    for q in (p[0], p[-1]):
        d = cl.distance(Point(q))
        if d > 0.6: free.append((q.round(1), round(d,1)))
print("hatch ends not on a drawn centreline:", len(free), "of", 2*len(hatch))
for q in free[:40]: print("  ", q)
