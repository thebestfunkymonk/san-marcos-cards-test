import sys
sys.path.insert(0, '.')
from shapely.geometry import Point, box
from deck import courtkit as K
from deck.motifs import core as C
import importlib
QH = importlib.import_module('art.QH')
sc = QH.figure()
zone = box(412, 178, 430, 208)
for it in sc.items:
    for m in it.frag.marks:
        if m.kind == 'fill' or not m.d: continue
        g = K.G.to_shape(m.d, tol=0.05) if False else None
        try:
            for pts, _ in K.G.flatten(m.d, 0.1):
                from shapely.geometry import LineString
                if len(pts) < 2: continue
                ln = LineString(pts)
                if ln.intersects(zone):
                    seg = ln.intersection(zone)
                    print(it.name, m.role, m.layer, getattr(m,'width',None), round(seg.length,1), [tuple(round(v,1) for v in c) for c in list(seg.coords)[:1]] if seg.geom_type=='LineString' else seg.geom_type)
        except Exception as e:
            print('err', it.name, e)
print('--- occ items covering (421,193)')
for it in sc.items:
    if it.occ is not None and it.occ.contains(Point(421,193)):
        print('occ', it.name)
res = sc.compose()
print('--- composed')
from shapely.geometry import LineString
for m in res.marks:
    if m.kind=='fill' or not m.d: continue
    for pts,_ in K.G.flatten(m.d,0.1):
        if len(pts)<2: continue
        ln=LineString(pts)
        if ln.intersects(zone):
            seg=ln.intersection(zone)
            print(m.role, m.layer, getattr(m,'width',None), round(seg.length,1), seg.bounds)
print('heal log near:')
for e in sc.heal_log:
    s=str(e)
    print(s[:200])
print('=== heal entries near far temple')
for e in sc.heal_log:
    at = e.get('at') if isinstance(e, dict) else None
    if at and 405 <= at[0] <= 440 and 170 <= at[1] <= 215:
        print(e)
print('=== items after head:')
names=[it.name for it in sc.items]
i=names.index('head'); print(names[i:])
for it in sc.items[i+1:]:
    if it.occ is not None and it.occ.distance(Point(422,193))<6: print('near occ', it.name, it.occ.distance(Point(422,193)), it.halo)
res2 = sc.compose(heal_gaps=False)
for m in res2.marks:
    if m.kind=='fill' or not m.d or m.role!='outline': continue
    for pts,_ in K.G.flatten(m.d,0.1):
        if len(pts)<2: continue
        ln=LineString(pts)
        if ln.intersects(zone):
            seg=ln.intersection(zone); print('noheal outline', round(seg.length,1), seg.bounds)
