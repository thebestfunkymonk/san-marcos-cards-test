from rh import *
import copy
from deck.motifs import fauna as FA
from inkkit import geom as G
orig = copy.deepcopy(FA.DARTER)
for x1, sx1 in ((22.0, 24.0), (22.0, 30.0), (24.0, 34.0)):
    FA.DARTER["stitch"]["x1"] = x1
    FA.DARTER["saddles"]["x1"] = sx1
    f = FA.fountain_darter(0, 0, 100)
    st = [p for m in f.marks if m.role == "stitch" for p, _ in G.flatten(m.d)]
    sad = [p for m in f.marks if m.role == "saddle" for p, _ in G.flatten(m.d)]
    print(f"stitch x1={x1}, saddles x1={sx1}: dashes {len(st)}, saddles {len(sad)} lens {[round(abs(p[-1][1]-p[0][1]),1) for p in sad]}, warnings {f.meta.get('warnings')}")
FA.DARTER["stitch"]["x1"] = 22.0; FA.DARTER["saddles"]["x1"] = 30.0
show(FA.fountain_darter(0, 0, 100), "darter100-fullstitch-8x", zoom=8)
FA.DARTER.clear(); FA.DARTER.update(orig)
