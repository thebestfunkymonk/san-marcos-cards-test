import sys, warnings
sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import numpy as np
from shapely.geometry import LineString
from deck import courtkit as K
from art import KD, _kd_body as B
WR = tuple(K.fist_wrist((KD.KEY_X, 384.0), -90.0, bend=KD.ARM_R["bend"], dist=KD.ARM_R["dist"], **KD.KEY_FIST))
h0 = K.fist((KD.KEY_X, 384.0), -90.0, wrist=WR, wrist_w=26.0, hand="L", **KD.KEY_FIST)
h1 = B.refine_fist(h0, (KD.KEY_X, 384.0), -90.0, fkw=KD.KEY_FIST)
def region(g, cx, cy, r=9, W=1.0, tag=''):
    ring = LineString(g.exterior.coords); L = ring.length
    def P(s): return np.array(ring.interpolate(s % L).coords[0])
    out=[]
    for s in np.arange(0, L, 0.4):
        p = P(s)
        if np.hypot(p[0]-cx, p[1]-cy) > r: continue
        v1, v2 = p - P(s-W), P(s+W) - p
        t = np.degrees(np.arctan2(v1[0]*v2[1]-v1[1]*v2[0], v1@v2))
        if abs(t) > 8: out.append(f'({p[0]:.1f},{p[1]:.1f}) {t:5.1f}')
    print(tag, out)
region(h0.hand.shape, 529, 405, tag='raw')
region(h1.hand.shape, 529, 405, tag='refined')
sc = KD.figure()
it = {i.name: i for i in sc.items}
region(it['handR'].occ, 529, 405, tag='scene')
print(h0.hand.shape.bounds, h1.hand.shape.bounds)
# replicate tucked on a scene without hands
import copy
sc2 = KD.figure()
names = [i.name for i in sc2.items]
idx = names.index('handL')
sc2.items = sc2.items[:idx]
hp = h1.tucked(sc2)
print('tucked meta tucked?', hp.meta.get('tucked'))
region(hp.shape, 529, 405, tag='tucked')
rb = h1.hand.meta['rebuild']
from deck.courtkit import _arm_dir
calls = []
orig = h1.hand.meta['rebuild']
def spy(u):
    calls.append(u); p = orig(u); region(p.shape, 529, 405, tag=f'rebuilt u={np.round(u,3)}'); return p
h1.hand.meta['rebuild'] = spy
hp = h1.tucked(sc2)
print('rebuild calls', len(calls), 'wrist_dir', h1.wrist_dir)
