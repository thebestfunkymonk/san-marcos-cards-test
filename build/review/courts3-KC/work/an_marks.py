import sys; sys.path.insert(0,'.')
import numpy as np, json
from shapely.geometry import Point
from deck import courtkit as K
from art import KC
opts = json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
pts = [tuple(map(float, s.split(','))) for s in sys.argv[2:]]
sc = KC.figure(opts)
res = sc.compose()
for (x,y) in pts:
    print('== near', x, y)
    p = Point(x,y)
    for m in res.marks:
        if not m.d: continue
        g = K.R(K.G.from_skia(m.skia()))
        if g.distance(p) < 2.0:
            print('  ', m.kind, m.role, m.w, m.layer, m.cap if hasattr(m,'cap') else '', round(g.distance(p),2))
            if m.kind!='fill':
                for ln in K._stroke_lines(m.d):
                    if ln.distance(p) < 4:
                        c = np.asarray(ln.coords)
                        ends = [c[0], c[-1]]
                        closed = np.allclose(c[0], c[-1])
                        print('      line len %.1f closed %s ends %s' % (ln.length, closed, [np.round(e,1).tolist() for e in ends]))
