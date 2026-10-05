import sys; sys.path.insert(0,".")
import numpy as np, shapely
from shapely.geometry import Point, LineString
from inkkit import geom as G
from deck.motifs import lion as L, rice as R, geometric as M, core as C
from deck.motifs import sheet_figurative as SF
def dangling(f, tol=1.3, name=""):
    lines = []
    for m in f.marks:
        if m.kind != "stroke" or m.role == "hatch": continue
        for pts, cl in G.flatten(m.d, 0.1):
            if len(pts) > 1: lines.append(LineString(pts))
    for m in f.marks:
        if m.kind == "fill":
            lines.append(G.to_shape(m.d, tol=0.1).boundary)
    U = shapely.union_all(lines)
    tot = bad = 0; where = []
    for m in f.marks:
        if m.role != "hatch": continue
        for pts, cl in G.flatten(m.d, 0.1):
            for p in (pts[0], pts[-1]):
                tot += 1
                dd = U.distance(Point(p))
                if dd > tol:
                    bad += 1; where.append((round(p[0],1), round(p[1],1), round(dd,1)))
    print(f"{name:34s} hatch ends {tot:4d}  not on a contour {bad:4d}", where[:6])
p = L.lion_moleca_parts()
dangling(p["wings"], name="moleca wings (Track A spade)")
dangling(L.lion_andante(0,0), name="lion andante")
dangling(R.ribbon_leaf(0,60,-14,170,bend=(12,-12)), name="ribbon leaf")
dangling(M.stalactite(0,0), name="stalactite")
dangling(M.knee_crenellation(0,200,100,h=50), name="knee crenellation")
dangling(M.source_rosette(375,525,130), name="rosette R130")
dangling(M.strata(shapely.box(0,0,120,80)), name="strata")
dangling(M.rowel_star(0,0,40), name="rowel star")
dangling(M.fault_plinth(375,500,60,hatch_step=1), name="fault plinth")
