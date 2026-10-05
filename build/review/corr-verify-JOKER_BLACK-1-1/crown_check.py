import sys, math
sys.path.insert(0, 'build/review/corr-verify-JOKER_BLACK-1-1'); sys.path.insert(0, '.'); sys.path.insert(0, 'art')
import numpy as np, shapely
from shapely.geometry import box
from shapes import load, shape_of
fn = sys.argv[1]; dx, dy = float(sys.argv[2]), float(sys.argv[3])
L = load(fn)
win = box(400, 150, 540, 300) if dy > 0 else box(400, 60, 540, 230)
gold = [shape_of(i) for i in L['gold'] if 'joker' not in i['cls']]
gold = shapely.union_all(gold)
cor = gold.intersection(box(430, 40, 540, 300))
cor_parts = [g for g in getattr(cor, 'geoms', [cor]) if g.area > 50]
cor = max(cor_parts, key=lambda g: g.area)
print('coronet area', round(cor.area, 2), 'holes', len(cor.interiors) if cor.geom_type == 'Polygon' else '?', 'bounds', [round(v, 1) for v in cor.bounds])
ink = shapely.union_all([shape_of(i) for i in L['ink'] if 'index' not in i['cls']])
near = ink.intersection(cor.buffer(30))
print('ink near coronet: min dist', round(ink.distance(cor), 3), 'overlap', round(ink.intersection(shapely.Polygon(cor.exterior)).area, 3))
for g in getattr(near, 'geoms', [near]):
    print('  ink piece (clipped to cor+30)', round(g.area, 1), [round(v, 1) for v in g.bounds])
# whole ink pieces near the crown
for g in getattr(ink, 'geoms', [ink]):
    if g.distance(cor) < 10:
        mic = shapely.maximum_inscribed_circle(g, 0.01)
        print('  whole ink piece', round(g.area, 1), [round(v, 1) for v in g.bounds], 'max inscribed r', round(mic.length, 2))
# reference: whole coronet from props
import _joker_black_props as PR
ref = PR.coronet()
ref = shapely.affinity.translate(ref, dx, dy)
print('ref coronet area', round(ref.area, 2), 'sym diff vs output', round(ref.symmetric_difference(cor).area, 3))
hull = shapely.affinity.translate(PR.coronet_hull(), dx, dy)
print('ink ∩ hull', round(ink.intersection(hull).area, 3), 'ink dist to hull', round(ink.distance(hull), 3))
