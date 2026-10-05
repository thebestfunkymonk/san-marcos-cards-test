import math, numpy as np
from shapely.geometry import LineString, Point
from deck.motifs import core as C
from deck.motifs import lion as LI
from deck.motifs.sheet_figurative import spade_live, spade_h13
for name, sil_d in (("trackA", spade_live()), ("h13", spade_h13())):
    sil = C.region(sil_d)
    ins = sil.buffer(-(12 + 2.1/2))
    x0,y0,x1,y1 = sil.bounds
    print(name, "bounds", [round(v,1) for v in sil.bounds], "width", round(x1-x0,1))
    for yy in (200, 262, 300, 335):
        ln = sil.intersection(LineString([(0,yy),(750,yy)]))
        print("  width at y", yy, round(ln.length,1))
    hx, hy = 375, 262
    for a in (-60,-40,-20,0,20,40,60,76):
        u = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
        ray = LineString([(hx,hy),(hx+u[0]*400, hy+u[1]*400)])
        g = ray.intersection(ins)
        # distance along ray to leave the inset
        L = max((Point(hx,hy).distance(Point(c)) for geom in getattr(g,'geoms',[g]) for c in geom.coords), default=0)
        print(f"  ray {a:4d} deg: inset boundary at r={L:6.1f}  room beyond mane(61.05)={L-61.05:6.1f}")
    # wing root actually used
    parts = LI.lion_moleca_parts(375, 262, silhouette=sil_d)
    w = parts["wings"]
    right = w.shape().intersection(__import__('shapely').box(375,0,750,1050))
    mane = parts["mane"].shape()
    print("  wing-to-mane min distance (px):", round(right.distance(mane.intersection(__import__('shapely').box(375,0,750,1050))),2))
    arm = w.select(lambda m: m.role=="arm")
    pts = np.vstack([np.asarray(p) for p,_ in __import__('inkkit.geom',fromlist=['x']).flatten(arm.marks[0].d)])
    pr = pts[pts[:,0]>375]
    i = np.argmax(pr[:,1])
    print("  arm (leading edge) right: y range", round(pr[:,1].min(),1), round(pr[:,1].max(),1), " lowest pt", pr[i].round(1))
    print("  wrist", [round(v,1) for v in parts["meta"]["wrist"]])
