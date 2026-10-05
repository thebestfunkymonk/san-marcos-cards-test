import sys, math, re
sys.path.insert(0, '.')
import numpy as np, shapely
from shapely import affinity
import xml.etree.ElementTree as ET
from inkkit import geom as G
import art.JOKER_RED as J
from art import _joker_red_pig as PIG, _joker_red_pose as P
dx, dy = J.FIG_SHIFT
t = ET.parse('cards/JOKER-RED.svg'); ns='{http://www.w3.org/2000/svg}'
def layer(lid, fill_only=True):
    g = [e for e in t.getroot() if e.get('id') == lid][0]
    shapes = []
    for p in g.iter(ns+'path'):
        if p.get('fill') not in (None, 'none'):
            shapes.append(G.to_shape(p.get('d'), tol=0.02))
        elif p.get('stroke'):
            w = float(p.get('stroke-width'))
            ls = G.to_shape(p.get('d'), tol=0.02) if False else None
    return shapely.union_all(shapes)
gold = layer('gold'); red = layer('red')
ds = PIG.collar_dags()
ctr, R, ax = PIG.collar_frame()
print('collar frame ctr', ctr + (dx,dy), 'R', R, 'axis', ax)
for i, (tri, bell, hole, bc, th) in enumerate(ds):
    want = tri.union(bell).difference(hole)
    want = affinity.translate(want, dx, dy)
    miss = want.difference(gold.buffer(0.05)).area
    extra_hole = affinity.translate(hole, dx, dy).intersection(gold).area
    # symmetry check of gold around dag axis within the dag region
    bcs = np.array(bc) + (dx, dy)
    print(f'dag {i}: heading {th:.2f}, bell centre ({bcs[0]:.1f},{bcs[1]:.1f}), missing gold {miss:.3f} px2, gold in hole {extra_hole:.3f}, red dist {want.distance(red):.2f}')
# spacing of bell centres
b = [np.array(bc) for *_, bc, _ in ds]
print('bell spacing', [round(float(np.hypot(*(b[i+1]-b[i]))),2) for i in range(4)])
# collar gold polygon: count pieces near collar
col = gold.intersection(shapely.box(320, 390, 470, 510))
print('collar gold pieces', [round(g.area,1) for g in getattr(col,'geoms',[col])])
print('collar bounds', col.bounds)
# min gold to red in collar area
print('collar gold to red dist', col.distance(red))
print('---- band')
dagsU = shapely.union_all([affinity.translate(tri.union(bell), dx, dy) for tri, bell, *_ in ds])
band = col.difference(dagsU.buffer(0.3))
c = np.array(ctr) + (dx, dy)
angs = []
for g in getattr(band,'geoms',[band]):
    xy = np.array(g.exterior.coords)
    a = np.degrees(np.arctan2(xy[:,1]-c[1], xy[:,0]-c[0]))
    r = np.hypot(xy[:,0]-c[0], xy[:,1]-c[1])
    print('band piece area %.1f angle %.2f..%.2f  r %.2f..%.2f' % (g.area, a.min(), a.max(), r.min(), r.max()))
    angs += [a.min(), a.max()]
print('fan dag headings 45.43..78.17 ; dag half-base angle', math.degrees(P.DAG_BASE/2/(R+P.COLLAR_W/2)))
lo, hi = min(angs), max(angs)
print('band overhang beyond fan: ear side %.2f deg (%.1f px), leg side %.2f deg (%.1f px)' % (45.43-lo, math.radians(45.43-lo)*R, hi-78.17, math.radians(hi-78.17)*R))
# band width along the arc: sample radial width
for a in np.linspace(lo+0.5, hi-0.5, 9):
    d = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
    ln = shapely.LineString([c + d*(R-20), c + d*(R+5)])
    s = ln.intersection(col)
    print('  angle %.1f band radial gold length %.2f' % (a, s.length))
