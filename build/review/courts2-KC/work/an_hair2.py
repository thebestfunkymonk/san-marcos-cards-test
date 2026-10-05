import sys, numpy as np
sys.path.insert(0,'.')
from deck import courtkit as K
from art import KC, _kc_beard as KB
from shapely.geometry import LineString, Point
import shapely
fc = K.face(KC.HEAD, "frontal", age="elder", **KC.FACE)
head = K.R(fc.head)
mo = K.moustache(fc, K.MoustacheSpec(root=(-1.5, 8.5), tip=(-32.0, 30.0), arch=7.0))
bd = KB.spray_lines_beard(fc, mo, **KC.BEARD)
front = shapely.union_all([head, bd.shape, mo.shape])
def check(top, bulge, bottom, ribbons=4):
    hs = K.HairSpec(top=top, bulge=bulge, bottom=bottom, ribbons=ribbons)
    hp = K.hair_fall(fc, -1, hs)
    k = 0
    for m in hp.lines.marks:
        if m.role != 'current': continue
        for l in K._stroke_lines(m.d):
            vis = l.difference(front)
            # min distance of visible centreline to front boundary, per y band
            ds = []
            for g in K._lines_of(vis):
                c = np.asarray(g.coords)
                for x,y in c[::4]:
                    ds.append((y, front.boundary.distance(Point(x,y))))
            ds = np.array(ds)
            if len(ds)==0: print('  line',k,'hidden'); k+=1; continue
            lo = ds[ds[:,1] < 7.0]
            print(f'  line {k}: vis y {ds[:,0].min():.0f}-{ds[:,0].max():.0f} min d {ds[:,1].min():.2f}',
                  'close ys:', (f'{lo[:,0].min():.0f}-{lo[:,0].max():.0f}' if len(lo) else '-'))
            k+=1
for spec in [((-52,-30),(-64,40),(-53,110)), ((-53,-30),(-65,40),(-54,110)), ((-53.5,-30),(-65.5,40),(-54.5,110)), ((-54,-30),(-66,40),(-55,110))]:
    print(spec); check(*spec)
