import sys, os, warnings
ROOT = '/home/luke/Projects/design/san-marcos-deck'
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + '/build/review/courts2-KH/work'); os.chdir(ROOT); warnings.simplefilter('ignore')
import numpy as np, shapely
from geomplot import plot
from deck import courtkit as K
from deck.motifs import core as C
import art.KH as KH, art._kh_parts as KP, art._kh_hands as KHN
box = eval(sys.argv[2]); outp = sys.argv[1]
for m in sys.argv[3:]:
    exec(m, {'KH': KH, 'K': K, 'np': np, 'KP': KP, 'KHN': KHN})
sc = KH.figure()
items = []
cols = {'robe': ('#a33', 'none'), 'sleeveL': ('green', 'green'), 'sleeveR': ('green', 'green'), 'cuffL': ('darkgreen', 'teal'),
        'cuffR': ('darkgreen', 'teal'), 'handL': ('orange', 'yellow'), 'handR': ('orange', 'yellow'), 'chalice': ('brown', 'none'), 'pole': ('brown', 'none')}
for it in sc.items:
    if it.name in cols and it.occ is not None:
        items.append((it.occ, cols[it.name][0], cols[it.name][1], 0.4))
# rings: the paper holes in the robe's red fill
robe = [it for it in sc.items if it.name == 'robe'][0]
for m in robe.frag.marks:
    if m.layer == 'red':
        g = K.R(C.Frag([m]).outline())
        for p in K._polys_of(g):
            for r in p.interiors:
                items.append((shapely.LinearRing(r), 'blue', 'none', 0.3))
plot(items, box, outp, scale=10, grid=5)
