import sys, ast
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qs/tools")
from r import render, montage
from deck import courtkit as K
from deck.motifs import core as C
import numpy as np
import art.QS as QS
import art._qs_parts as Q
variants = eval(sys.argv[2])
outs = []
for i, v in enumerate(variants):
    hg = QS.head_group()
    fn = v.pop("fn", "fringe")
    circ = v.pop("circ", QS.CIRCLET)
    if fn == "fringe":
        d = Q.fringe_circlet(*circ, clip=hg["veil"].buffer(-1.0), **v)
    else:
        d = Q.stalactite_circlet(*circ, clip=hg["veil"].buffer(-1.0), **v)
    arc = np.asarray(d.meta["arc"])
    from shapely.geometry import Polygon
    above = Polygon(np.vstack([arc, [[arc[-1][0] + 80, arc[-1][1]], [arc[-1][0] + 80, 0], [arc[0][0] - 80, 0],
                                     [arc[0][0] - 80, arc[0][1]]]])).buffer(0)
    dome = hg["veil"].intersection(above)
    sc = K.Scene()
    sc.part("veil", K.Part(hg["veil"], C.Frag(), K.outline(hg["veil"]), {}))
    for k in ("neck", "lf", "ln", "head"):
        sc.part(k, hg[k])
    sc.part("dome", K.Part(dome, C.Frag(), C.Frag(), {}))
    sc.part("diad", d)
    lay = sc.layers()
    o = f"{sys.argv[1]}-{i}.png"
    render(lay, o, (310, 110, 490, 250), 3)
    outs.append(o)
    render(lay, f"{sys.argv[1]}-{i}s.png", (310, 110, 490, 250), 1)
montage(outs, sys.argv[1] + ".png", tile="2x")
