import sys, math
V='build/review/corr-verify-JOKER_BLACK-2-0'
sys.path.insert(0,'.'); sys.path.insert(0,'art'); sys.path.insert(0,V)
import shapely, shapely.affinity as AF, numpy as np
import _joker_black_props as PR, _joker_black_plumage as PL, _joker_black_pose as P
from shapes import layer_paths
from inkkit import geom as G
L=layer_paths('cards/JOKER-BLACK.svg')
out=G.to_shape(L['gold'][1][1], tol=0.01)
ref=PR.coronet(); refc=PL.clean(ref, keep=ref)
refc=AF.translate(refc,*PR.FIG_SHIFT); ref=AF.translate(ref,*PR.FIG_SHIFT)
print('out vs clean(ref) symdiff %.3f'%out.symmetric_difference(refc).area, 'out vs raw ref symdiff %.3f'%out.symmetric_difference(ref).area)
print('BILL_TIP draft', P.BILL_TIP, 'card', (P.BILL_TIP[0]+PR.FIG_SHIFT[0], P.BILL_TIP[1]+PR.FIG_SHIFT[1]))
body, holes, balls = PR._cor_local()
tf=lambda g: AF.translate(AF.translate(AF.rotate(AF.translate(g,-PR.COR_HOOK[0],-PR.COR_HOOK[1]),PR.COR_SWING,origin=(0,0)),*P.BILL_TIP),*PR.FIG_SHIFT)
bird=G.to_shape(L['ink'][0][1], tol=0.01)
H=PR.BAND_H
for (px,h,ball) in PR.POINTS:
    yb=PR._band_y(px,-H)+0.8
    tri=shapely.Polygon([(px-4.6,yb),(px,yb-h-2),(px+4.6,yb)])
    t=tf(tri)
    print('point x=%5.1f ball=%s  dist to bird %.2f  overlap %.3f'%(px,ball,t.distance(bird),t.intersection(bird).area))
for b in balls:
    bp=tf(shapely.Point(*b).buffer(3.15))
    print('ball', b, 'dist %.2f'%bp.distance(bird))
for jx in (-15,0,15):
    jy=PR._band_y(jx,-H/2)
    j=tf(shapely.Polygon([(jx-4.4,jy),(jx,jy-3.2),(jx+4.4,jy),(jx,jy+3.2)]))
    print('jewel',jx,'dist %.2f'%j.distance(bird), 'jewel+3 gold ring dist %.2f'%j.buffer(3).distance(bird))
# how the wedge of paper between bill and crown rim widens with distance from tip
tip=np.array([446.4,193.06])
for d in [1,2,3,4,6,8,10,12,15]:
    c=shapely.Point(*tip).buffer(d).exterior
    # gap along the circle between bill and crown: find arc points not in either
    pts=np.array(c.coords)
    # sample finer
    ang=np.linspace(0,2*np.pi,3600)
    P2=np.column_stack([tip[0]+d*np.cos(ang),tip[1]+d*np.sin(ang)])
    inb=np.array([bird.contains(shapely.Point(*p)) for p in P2]); inc=np.array([out.contains(shapely.Point(*p)) for p in P2])
    # lower half only (y>tip)
    free=~inb & ~inc & (P2[:,1]>tip[1])
    # find contiguous free run between bird and crown
    runs=[];cur=None
    for i,f in enumerate(free):
        if f and cur is None: cur=i
        if not f and cur is not None: runs.append((cur,i)); cur=None
    lens=[(e-s)*(2*np.pi*d/3600) for s,e in runs]
    print('r=%2d paper arcs below tip (px): %s'%(d, ['%.2f'%l for l in lens]))
