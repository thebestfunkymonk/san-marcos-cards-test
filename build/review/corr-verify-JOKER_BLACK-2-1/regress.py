import sys
sys.path.insert(0, 'build/review/corr-verify-JOKER_BLACK-2-1'); sys.path.insert(0, '.')
import shapely, shapely.affinity as AF
from shapely.geometry import box, Point
from shapes import load, shape_of
G = load('build/gallery/svg/JOKER-BLACK.svg')
O = load('build/review/corr-verify-JOKER_BLACK-2-1/orig_preview/JOKER-BLACK.svg')
N = load('cards/JOKER-BLACK.svg')
dx, dy = -8.4, 72.8
def summary(L, name):
    print(name, {k: len(v) for k, v in L.items()})
summary(G,'gallery'); summary(O,'orig-preview'); summary(N,'now')
# gallery vs orig preview: bird solid identical?
gb = shape_of(G['ink'][0]); ob = shape_of(O['ink'][0]); nb = shape_of(N['ink'][0])
print('gallery vs orig bird symdiff', round(gb.symmetric_difference(ob).area,3))
nbs = AF.translate(nb, -dx, -dy)
sd = gb.symmetric_difference(nbs)
print('gallery bird vs now bird (unshifted) symdiff', round(sd.area,3), [round(v,1) for v in sd.bounds] if not sd.is_empty else None)
for g in sorted(getattr(sd,'geoms',[sd]), key=lambda g:-g.area)[:5]:
    print('  piece', round(g.area,3), [round(v,2) for v in g.bounds])
print('holes: gallery', len(gb.interiors), 'now', len(nb.interiors))
# jade
gj = shape_of(G['jade'][0]); nj = AF.translate(shape_of(N['jade'][0]), -dx, -dy)
print('jade symdiff', round(gj.symmetric_difference(nj).area,3))
# eye ring gold 0
print('eye gold symdiff', round(shape_of(G['gold'][0]).symmetric_difference(AF.translate(shape_of(N['gold'][0]),-dx,-dy)).area,3))
# rays
for i in range(len(G['ink'])):
    it = G['ink'][i]
    print('gal ink', i, it['cls'], it['sw'], [round(v,1) for v in shape_of(it).bounds])
