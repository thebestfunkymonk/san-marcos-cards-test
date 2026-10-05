from rv import *
from deck.motifs import *
from deck.motifs import fauna
from inkkit import geom as G
from shapely.geometry import LineString, Point
import numpy as np, itertools
# rebuild plumes individually by monkeypatching gill_plume to record frags
recs=[]
orig=fauna.gill_plume
def rec(*a, **k):
    f=orig(*a, **k); recs.append(f); return f
fauna.gill_plume=rec
s=fauna.blind_salamander(0,0, centre=False)
fauna.gill_plume=orig
print(len(recs), "plumes")
def lines(f, role):
    return [LineString(p) for m in f.marks if m.role==role for p,c in G.flatten(m.d,0.05)]
cross=0
for i,j in itertools.combinations(range(len(recs)),2):
    A=lines(recs[i],"spine")+lines(recs[i],"barb"); B=lines(recs[j],"spine")+lines(recs[j],"barb")
    for a in A:
        for b in B:
            if a.intersects(b): cross+=1
print("inter-plume stroke crossings (no interlace gap):", cross)
# plume length vs head
for f in recs[:3]:
    sp=[m for m in f.marks if m.role=="spine"][0]
    pts=G.flatten(sp.d,0.05)[0][0]; print("plume spine length", round(G.Curve(pts).length,1))
L=s.meta["length"]; print("head length (snout->gill station 0.128L)", round(0.128*L,1), "head width ~", 2*14.2*(L/300)**0.5)
