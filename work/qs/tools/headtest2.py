"""head-group test: headtest2.py OUT [variant python-literal dict of face kw]"""
import sys, ast
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qs/tools")
from r import render, montage
from deck import courtkit as K
from deck.motifs import core as C
import art.QS as QS
import art._qs_face as QF
import art._qs_parts as Q

outs = []
variants = ast.literal_eval(sys.argv[2]) if len(sys.argv) > 2 else [{}]
for i, v in enumerate(variants):
    fkw = dict(eye_dy=11.0, mouth_dy=33.0, lip_dy=40.0, lip_sag=-1.4, lip_hw=4.6, brow_in=8.0)
    fkw.update(v)
    orig = QF.oracle_face
    QS.QF = type("M", (), {"oracle_face": staticmethod(lambda c, **kw: orig(c, **{**kw, **v}))})
    hg = QS.head_group()
    QS.QF = QF
    R_ = lambda p: Q.rot_part(p, QS.TILT, QS.PIVOT)
    rg = lambda g: Q.rot_geom(g, QS.TILT, QS.PIVOT)
    sc = K.Scene()
    sc.part("veil", K.Part(rg(hg["veil"]), C.Frag(), K.outline(rg(hg["veil"])), {}))
    for k in ("neck", "lf", "ln", "head"):
        sc.part(k, R_(hg[k]))
    sc.part("dome", K.Part(rg(hg["dome"]), C.Frag(), K.outline(rg(hg["dome"])), {}))
    sc.part("diad", R_(hg["diad"]))
    o = f"{sys.argv[1]}-{i}.png"
    render(sc.layers(), o, (300, 110, 500, 300), 3)
    outs.append(o)
montage(outs, sys.argv[1] + ".png", tile=f"{min(len(outs),4)}x")
