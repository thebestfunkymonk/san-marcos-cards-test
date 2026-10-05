import sys; sys.path.insert(0,'.')
exec(open(sys.argv[1]).read().split("print('---- band')")[0].replace("print(", "(lambda *a, **k: None)("))
pig = PIG.build()
sil = affinity.translate(pig['sil'], dx, dy)
paper_in = sil.difference(red).difference(gold)
exp = col.buffer(4.2, quad_segs=24)
extra = paper_in.difference(exp.buffer(0.15)).intersection(exp.buffer(10))
parts = [g for g in getattr(extra,'geoms',[extra]) if g.area > 0.5]
for g in sorted(parts, key=lambda g: -g.area):
    print('extra paper near ground: area %.1f at (%.1f, %.1f) bounds %s' % (g.area, g.centroid.x, g.centroid.y, tuple(round(v,1) for v in g.bounds)))
# where ground expected but red/other present
short = exp.difference(col).intersection(sil).intersection(red)
print('red inside expected ground: %.3f' % short.area)
# render diagnostic
from PIL import Image, ImageDraw
sc = 6; x0, y0, x1, y1 = 320, 385, 475, 515
im = Image.open(sys.argv[2]).convert('RGB').crop((x0*sc, y0*sc, x1*sc, y1*sc))
dr = ImageDraw.Draw(im, 'RGBA')
for g in parts:
    dr.polygon([((x-x0)*sc, (y-y0)*sc) for x, y in g.exterior.coords], fill=(255,0,255,160))
ee = exp.exterior if exp.geom_type=='Polygon' else None
for poly in getattr(exp,'geoms',[exp]):
    dr.line([((x-x0)*sc, (y-y0)*sc) for x, y in poly.exterior.coords], fill=(0,120,255,255), width=2)
im.save(sys.argv[3])
