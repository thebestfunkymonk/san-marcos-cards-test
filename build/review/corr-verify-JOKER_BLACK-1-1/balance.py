import sys
sys.path.insert(0, 'build/review/corr-verify-JOKER_BLACK-1-1'); sys.path.insert(0, '.')
import shapely
from shapely.geometry import box
from shapes import load, shape_of
fn = sys.argv[1]
L = load(fn)
ink = shapely.union_all([shape_of(i) for i in L['ink'] if 'index' not in i['cls']])
gold = shapely.union_all([shape_of(i) for i in L['gold'] if 'joker' not in i['cls']])
jade = shapely.union_all([shape_of(i) for i in L['jade']])
pieces = sorted(getattr(ink, 'geoms', [ink]), key=lambda g: -g.area)
bird = pieces[0]
print('largest ink piece', round(bird.area,1), [round(v,1) for v in bird.bounds])
for g in pieces[1:12]:
    print('  other ink', round(g.area,1), [round(v,1) for v in g.bounds])
# crown + eye ring = gold pieces within bird bbox region above wire
gp = list(getattr(gold, 'geoms', [gold]))
for g in gp: print('  gold', round(g.area,1), [round(v,1) for v in g.bounds])
bx = bird.bounds
tip = [g for g in pieces[1:] if g.area < 40 and g.bounds[1] < bx[1]+5 or (g.bounds[3] < bird.bounds[1]+20 and g.area > 20 and g.area < 40)]
# bird+crown: bird solid + its tip piece + jade inside bird hull + gold not bulbs (y < wire top)
bird_hull = shapely.Polygon(bird.exterior)
crown_eye = [g for g in gp if g.area > 100 and g.bounds[3] < 300] + [g for g in gp if g.within(bird_hull.buffer(1))]
sel = [bird] + [g for g in pieces[1:] if g.area > 20 and g.area < 40 and g.bounds[3] < 300] + crown_eye + [jade]
u = shapely.union_all(sel)
print('bird+crown(+tip,+jade,+eye) area', round(u.area,1), 'centroid', round(u.centroid.x,2), round(u.centroid.y,2))
u2 = shapely.union_all([shapely.Polygon(bird.exterior)] + crown_eye)
print('silhouette (holes filled) + crown centroid', round(u2.centroid.x,2), round(u2.centroid.y,2), 'bounds', [round(v,1) for v in u2.bounds])
