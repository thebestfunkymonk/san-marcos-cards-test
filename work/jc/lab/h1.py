import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_face as F
import _jc_parts as J
import _jc_head as H
import _jc_body as B
FACE_LOWER = [(429, 207), (427, 234), (418, 256), (398, 273), (377, 280), (362, 275), (351, 259), (345, 234), (341, 207)]
def mk(outer, inner, **kw):
    def b():
        sc = K.Scene()
        fc = F.face_jc((385.0, 207.0), contour=FACE_LOWER, mouth=(-2.0, 37.0, 8.0, 10.0, 1.8, -1.0), lip=(-1.0, 44.5, 5.5, -1.8))
        sc.part("hair", H.pageboy(outer=outer, inner=inner, **kw))
        sc.part("neck", K.neck(fc, bottom=312.0, width=40.0))
        sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
        sc.part("collar", B.falling_collar())
        sc.part("ear", J.ear(fc))
        sc.part("cap", J.cap(fc, tip=(292.0, 171.0), top=(393.0, 106.0), flap_tip=(473.0, 130.0), hatband=10.5))
        return sc
    return b
V = json.loads(sys.argv[2])
run(sys.argv[1], [mk(**v) for v in V], box=(330, 150, 510, 330), width=360)
