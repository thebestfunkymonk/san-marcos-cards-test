import sys; sys.path.insert(0,'.')
import numpy as np, json
from art import _kc_robe as RB, KC
side, groove = int(sys.argv[1]), float(sys.argv[2])
orig = RB._groove
best = {}
def wrap(band, zone, ra, rb, rules, ang, v, origin):
    res = orig(band, zone, ra, rb, rules, ang, v, origin)
    if rules[0]['side'] == side and abs(rules[0]['groove'] - groove) < .1:
        if not best or res[0] > best['s']:
            best.update(s=res[0], o=origin, res=res, args=(band, zone, ra, rb, rules, ang, v))
    return res
RB._groove = wrap
KC.figure({})
print('best score', best['s'], 'origin', best['o'])
band, zone, ra, rb, rules, ang, v = best['args']
for k in range(1, len(rules) + 1):
    sc, a, b, hs = orig(band, zone, ra, rb, rules[:k], ang, v, best['o'])
    print(rules[k-1]['mode'], 'score %.2f' % sc, 'a', [(np.round(g.coords[0],1).tolist(), np.round(g.coords[-1],1).tolist()) for g in a],
          'b', [(np.round(g.coords[0],1).tolist(), np.round(g.coords[-1],1).tolist()) for g in b], 'nh', len(hs),
          'hy', [round(h.centroid.y,1) for h in sorted(hs, key=lambda h: h.centroid.y)][:6])
