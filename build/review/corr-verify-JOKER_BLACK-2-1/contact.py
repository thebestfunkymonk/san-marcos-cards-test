import sys
sys.path.insert(0, 'build/review/corr-verify-JOKER_BLACK-2-1'); sys.path.insert(0, '.')
import shapely, numpy as np
from shapely.geometry import box, Point, LineString
from shapes import load, shape_of
L = load(sys.argv[1] if len(sys.argv)>1 else 'cards/JOKER-BLACK.svg')
bird = shape_of(L['ink'][0]); cor = shape_of(L['gold'][1])
ov = bird.intersection(cor)
print('overlap area', round(ov.area,3), [round(v,2) for v in ov.bounds])
# tip = topmost point of bird
xs, ys = np.array(bird.exterior.coords).T
i = ys.argmin(); tip = (xs[i], ys[i]); print('tip', tip)
# gold left of bill near tip: gold within 12 px of tip minus bird
near = cor.intersection(Point(tip).buffer(12))
for g in getattr(near.difference(bird), 'geoms', [near.difference(bird)]):
    pass
# paper wedge between bill and crown: for each horizontal line y from tip down, the x-gap between bill right edge and crown left rim
for y in np.arange(193.0, 215.0, 1.0):
    ln = LineString([(420, y), (500, y)])
    b = ln.intersection(bird); c = ln.intersection(cor)
    bx = [g.bounds for g in getattr(b,'geoms',[b]) if not g.is_empty]
    cx = [g.bounds for g in getattr(c,'geoms',[c]) if not g.is_empty]
    print(round(y,1), 'bill x', [ (round(a[0],2), round(a[2],2)) for a in bx], 'crown x', [ (round(a[0],2), round(a[2],2)) for a in cx])
# distance between bill boundary and crown boundary along normal: compute min gap of paper region between them
paper = box(430,185,470,225).difference(bird).difference(cor)
# paper pieces narrow: erode by 1.25 (2.5 px width)
thin = paper.difference(paper.buffer(-1.25).buffer(1.25))
for g in sorted(getattr(thin,'geoms',[thin]), key=lambda g:-g.area)[:6]:
    print('thin paper (<2.5 px wide) piece', round(g.area,2), [round(v,2) for v in g.bounds])
gl = cor.difference(bird)
thin_g = gl.difference(gl.buffer(-0.75).buffer(0.75))
for g in sorted(getattr(thin_g,'geoms',[thin_g]), key=lambda g:-g.area)[:6]:
    print('thin gold (<1.5 px) piece', round(g.area,3), [round(v,2) for v in g.bounds])
# gold visible left of the bill's left edge near the tip
left = cor.difference(bird).intersection(box(430, 185, 447, 200))
print('gold in box left/above tip', round(left.area,2), [round(v,2) for v in left.bounds])
