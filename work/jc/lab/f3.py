import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_face as F
import _jc_parts as J
def mk(**kw):
    def b():
        sc = K.Scene()
        fc = F.face_jc((385.0, 207.0), **kw)
        sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
        sc.part("ear", J.ear(fc))
        sc.part("cap", J.cap(fc, tip=(292.0, 171.0), top=(393.0, 106.0), flap_tip=(473.0, 130.0), hatband=10.5))
        print("strokes", fc.strokes)
        return sc
    return b
V = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [{}]
run(sys.argv[1], [mk(**v) for v in V], box=(320, 170, 450, 300), width=390)
