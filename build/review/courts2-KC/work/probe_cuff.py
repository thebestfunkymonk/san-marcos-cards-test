import sys, json
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
from art import KC
from deck import courtkit as K
for js in sys.argv[1:]:
    o = json.loads(js)
    sc = KC.figure(o); sc.compose()
    hits = [e for e in sc.heal_log if 280 < e['at'][0] < 300 and 455 < e['at'][1] < 511]
    sl, cf = K.sleeve(K.SleeveSpec(**{**KC.SLEEVE_L, **o.get('sleeveL', {})}, wrist=tuple(o.get('wl', KC.CUP_WRIST)), folds=0, color=K.RED, cuff_color=K.JADE))
    print(js, 'cuff maxx', round(cf.shape.bounds[2],1), 'heal near stole edge:', [(e['action'], e['role'], e['at']) for e in hits])
