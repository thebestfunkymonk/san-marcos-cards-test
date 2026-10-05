import sys; sys.path.insert(0,'.')
import numpy as np
from shapely.geometry import Point
from art import _kc_robe as RB, KC
from deck import courtkit as K
orig = RB._groove
def wrap(band, zone, ra, rb, rules, ang, v, origin):
    res = orig(band, zone, ra, rb, rules, ang, v, origin)
    if rules[0]['side'] == 1 and rules[0]['groove'] == 101.0 and res[0] > -5:
        r = [x for x in rules if x['mode']=='land'][0]; obs = K.R(r['obstacle'])
        rays = {'a': res[1], 'b': res[2]}
        Js = {}
        for L in 'ab':
            for g in rays[L]:
                gc = np.asarray(g.coords); gc = gc if gc[0][1] < gc[-1][1] else gc[::-1]
                J = RB._first_hit(gc, obs)
                if J is not None: Js[L] = J; break
        print('score', res[0], 'J', {k: np.round(v_,1).tolist() for k, v_ in Js.items()}, 'corners', [np.round(c,1).tolist() for c in r['corners']])
        for h in res[3]:
            if h.bounds[3] < 420: continue
            hit = h.intersection(obs.boundary)
            hp = [np.round(np.asarray(g.coords[0]),1).tolist() for g in getattr(hit,'geoms',[hit])] if not hit.is_empty else []
            eb = RB._end_on(h, rays['b']); ea = RB._end_on(h, rays['a'])
            print('  h', np.round(np.asarray(h.coords),1).tolist(), 'land', hp, 'ea', None if ea is None else np.round(ea,1).tolist(), 'eb', None if eb is None else np.round(eb,1).tolist())
    return res
RB._groove = wrap
KC.figure({})
