from rv import *
from deck.motifs import *
from deck.motifs import lion as LI
from deck import frames
import numpy as np
from inkkit import geom as G
sp = frames.ace_pip_d('S')
print("spade bbox", G.bbox(sp))
p = LI.lion_moleca_parts(375, 262, silhouette=sp)
w = p["wings"]
print("wrist", p["meta"]["wrist"])
# covert extent
cov = w.select(lambda m: m.role=="covert")
print("covert bbox", [round(v,1) for v in cov.bbox()])
arm = w.select(lambda m: m.role=="arm")
print("arm bbox", [round(v,1) for v in arm.bbox()])
print("mane bbox", [round(v,1) for v in p["mane"].bbox()], "vent bbox", [round(v,1) for v in p["vent"].bbox()])
# measure spade widths
from shapely.geometry import LineString
from deck.motifs.core import region
g = region(sp)
for y in (200, 262, 335, 345):
    ln = g.intersection(LineString([(0,y),(750,y)]))
    print("y", y, "width", round(ln.length,1), [round(v,1) for v in ln.bounds])
print("spade height", G.bbox(sp)[3]-G.bbox(sp)[1])
