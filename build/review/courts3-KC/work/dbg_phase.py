import sys; sys.path.insert(0,'.')
import numpy as np
from art import _kc_robe as RB, KC
orig = RB._groove
def wrap(band, zone, ra, rb, rules, ang, v, origin):
    res = orig(band, zone, ra, rb, rules, ang, v, origin)
    kinds = [r['mode'] for r in rules]
    if any(r.get('phase') for r in rules):
        print(rules[0]['side'], rules[0]['groove'], kinds, 'origin', np.round(origin,2), 'score %.3f' % res[0], 'nh', len(res[3]))
    return res
RB._groove = wrap
KC.figure({})
