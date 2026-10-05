import sys, os, warnings
ROOT = '/home/luke/Projects/design/san-marcos-deck'
sys.path.insert(0, ROOT); os.chdir(ROOT); warnings.simplefilter('ignore')
import numpy as np, shapely
from shapely.geometry import LineString
from deck import courtkit as K
from deck.motifs import geometric as MG, core as C
from inkkit import geom as G
import art.KH as KH, art._kh_parts as KP
robe_m, rip, robe_inner = KP.robe(KH.ROBE, border=30.0, pitch=(96.0, 36.0), origin=(K.AX, 312.0))
lp = KP.trim_lapel(KH.LENS, 1, robe_m.shape, shoulder_x=KH.LAPEL_X, collar_sag=-4.0, r=11.0, bead_off=11.4)
reg = lp.shape
lo, hi = KH._pole_line()
pole = KP.pole(lo, hi, round_low=False, **KH.POLE_KW).shape
# other things in front of the right lapel near the pole: beard, hair, clasp, window (ignored: fixed)
r = 11.0
def graze(ox, oy, near=3.2):
    sc = MG.scale_lattice(reg, r, origin=(ox, oy))
    fin = pole.buffer(-0.3); fz = pole.buffer(near)
    tot = 0.0; n = 0
    for m in sc.marks:
        for pts, closed in G.flatten(m.d, 0.1):
            ln = LineString(pts)
            vis = ln.difference(fin)
            for comp in K._lines_of(shapely.line_merge(vis.intersection(fz))):
                if comp.length < 0.3: continue
                if comp.distance(pole) > 0.4 or comp.length > 2.2 * near:
                    tot += comp.length; n += 1
    return tot, n
base_o = (2 * K.AX - (KH.LENS.cx - r), 250.0)   # the mirrored left lapel's origin (x mirrored)
print('mirror-equivalent origin', base_o)
rows = []
for dx in np.arange(0, 2 * r, 1.0):
    for dy in np.arange(0, 0.6 * r * 2, 0.6):
        t, n = graze(base_o[0] + dx, base_o[1] + dy)
        rows.append((round(t, 1), n, dx, round(dy, 1)))
rows.sort()
print(rows[:12])
print('dx0dy0', [r_ for r_ in rows if r_[2] == 0 and r_[3] == 0])

def strip_info():
    S = reg.difference(pole)
    parts = sorted(K._polys_of(S), key=lambda g: -g.area)
    for g in parts:
        c = g.representative_point()
        # max inscribed width via erosion
        w = 0.0
        for e in np.arange(0.5, 30, 0.5):
            if g.buffer(-e).is_empty:
                w = 2 * e; break
        print('piece area', round(g.area, 1), 'rep', round(c.x, 1), round(c.y, 1), 'bounds', np.round(g.bounds, 1), 'max width ~', w)
