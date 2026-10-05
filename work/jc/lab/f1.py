import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_face as F
def mk(kind, **kw):
    def b():
        sc = K.Scene()
        if kind == "kit":
            fc = K.face((385.0, 207.0), "3/4-left", **kw)
        else:
            fc = F.face34((385.0, 207.0), **kw)
        sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
        return sc
    return b
run("f1", [mk("kit", age="young", lids="heavy", ears=True), mk("kit", age="young", lids="level", ears=True),
           mk("kit", age="young", lids="raised", ears=True, pupil_dx=-3),
           mk("mine", lids="level"), mk("mine", lids="heavy")], box=(320, 140, 450, 300), width=390)
