import sys, os, math, itertools
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import numpy as np
from shapely.geometry import LineString, Point
import QC
from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM
from inkkit import geom as G
sc, fc = QC.figure()
it = {i.name: i for i in sc.items}
hair = it['hairR'].occ; cloak = it['cloak'].occ
def _u(deg):
    a = math.radians(deg); return np.array([math.cos(a), math.sin(a)])
def evaluate(ay, h0, pieces, aw_, florets, tipf, x=541.0, rachis_hw=3.0, sd=-1, verbose=False):
    heading = -h0 if sd > 0 else 180.0 + h0
    turns = [(Lp, tr * sd) for (Lp, tr) in pieces]
    _, pts, t = FM.arc_path(x + sd * (rachis_hw - 1.0), ay, heading, turns)
    pts = np.asarray(pts, float); cv = G.Curve(pts)
    arm = LineString(pts).buffer(aw_ / 2, cap_style=1, quad_segs=12)
    fl = []
    for (fr, ped, L, W, hang) in florets:
        b = cv.at_s(cv.length * fr); u = _u(90.0 - sd * hang); b0 = b + u * (aw_ / 2 - 0.5); q = b0 + u * ped
        v = K.R(C.vesica_d(q - u * 1.0, q + u * L, W)); fl.append((v, b0))
    L, W = tipf; e = pts[-1]; tg = cv.tangent_s(cv.length); u = _u(math.degrees(math.atan2(tg[1], tg[0])))
    tip = K.R(C.vesica_d(e - u * (aw_ / 2 + 1.0), e + u * L, W))
    res = {}
    for i, (v, b0) in enumerate(fl):
        armx = arm.difference(Point(*b0).buffer(11.0))
        res[f'f{i}-arm'] = v.distance(armx)
    for i, j in itertools.combinations(range(len(fl)), 2):
        res[f'f{i}-f{j}'] = fl[i][0].distance(fl[j][0])
    for i, (v, b0) in enumerate(fl):
        res[f'f{i}-tip'] = v.distance(tip)
    allg = K.U(arm, tip, *[v for v, _ in fl])
    res['hair'] = allg.distance(hair); res['cloak'] = allg.distance(cloak.exterior)
    res['xmin'] = allg.bounds[0]; res['ymax'] = allg.bounds[3]
    return res
a0 = QC.SCEPTRE['arms'][0]
orig = (245.0, 62.0, ((18.0, 50.0), (32.0, 60.0), (12.0, 30.0)), 6.0,
        ((0.35, 7.0, 22.0, 7.6, 0.0), (0.61, 7.0, 22.0, 7.6, 0.0)), (22.0, 7.6))
def show(tag, args):
    r = evaluate(*args)
    print(tag, ' '.join(f'{k}={v:.1f}' for k, v in r.items()))
show('orig', orig)
show('cur ', a0)
if len(sys.argv) > 1:
    import json
    for line in sys.argv[1:]:
        show('try ', eval(line))
