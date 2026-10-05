from rv import *
from deck.motifs import *
from inkkit import geom as G
from shapely.geometry import LineString
import numpy as np, itertools
s = blind_salamander(0,0)
spines=[m for m in s.marks if m.role=="spine"]
print("spine marks", len(spines))
lines=[]
for m in spines:
    for pts,cl in G.flatten(m.d,0.05):
        lines.append(LineString(pts))
print("spine subpaths", len(lines))
for (i,a),(j,b) in itertools.combinations(enumerate(lines),2):
    x = a.intersection(b)
    if not x.is_empty:
        print("spines", i, j, "cross at", x.wkt[:80])
# also barbs vs other spines
barbs=[m for m in s.marks if m.role=="barb"]
bl=[LineString(p) for m in barbs for p,c in G.flatten(m.d,0.05)]
n=0
for i,a in enumerate(lines):
    for b in bl:
        x=a.intersection(b)
        if not x.is_empty and x.distance(__import__('shapely').geometry.Point(a.coords[0]))>1 :
            n+=1
print("barb/spine crossings (excluding own roots)", n)
# gill length vs head length
from deck.motifs.fauna import SALAMANDER
print("L", s.meta["length"])
