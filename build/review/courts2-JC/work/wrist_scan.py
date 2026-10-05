import sys, warnings; sys.path.insert(0,'.'); sys.path.insert(0,'art')
warnings.simplefilter('ignore')
from deck import courtkit as K
import JC, _jc_body as B
import numpy as np
from shapely.geometry import Point, LineString
torso = B.region(*JC.TORSO)
jer = B.region(*JC.JERK).intersection(torso)
bl = B.reed_belt(torso, y=440.0, h=24.0, sag=4.0, x0=220.0, x1=560.0, front=358.0)
bb = bl.shape.boundary
jb = jer.boundary.intersection(K.box(480, 380, 520, 470))
for fy in [float(a) for a in sys.argv[1].split(',')]:
  for bend in [float(a) for a in sys.argv[2].split(',')]:
    for dist in [float(a) for a in sys.argv[3].split(',')]:
        F=(548.0, fy)
        WR = tuple(K.fist_wrist(F, -90.0, bend=bend, dist=dist, **JC.FIST_KW))
        sc = K.Scene(rank='J')
        sl, cf = K.sleeve(K.SleeveSpec(wrist=WR, folds=0, **JC.SLEEVE_R_SPEC))
        sc.part('sleeveR', sl); sc.part('cuffR', cf)
        h = K.fist(F, -90.0, wrist=WR, wrist_w=26.0, hand='L', **JC.FIST_KW)
        hp = h.tucked(sc)
        hb = hp.shape.boundary.difference(cf.shape.buffer(0.5)).difference(sl.shape.buffer(0.5))
        d_j = hb.distance(jb); x_j = hb.intersects(jb)
        pts = np.asarray(cf.shape.exterior.coords)
        cd = min(bb.distance(Point(*p)) for p in pts)
        # cuff corner (lower-right) to belt edge
        c = pts[np.argmax(pts[:,0] + 0.3*pts[:,1])]
        print(f"fy {fy} bend {bend} dist {dist}: WR {np.round(WR,1)} hand-jerkin d {d_j:.1f} cross {x_j}; cuffcorner {np.round(c,1)} d_belt {bb.distance(Point(*c)):.1f}")
