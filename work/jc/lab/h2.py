import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_face as F, _jc_parts as J, _jc_head as H, _jc_body as B
FACE_LOWER = [(429, 207), (427, 234), (418, 256), (398, 273), (377, 280), (362, 275), (351, 259), (345, 234), (341, 207)]
V = json.loads(sys.argv[2])
def mk(v):
    def b():
        sc = K.Scene(rank="J")
        fc = F.face_jc((385.0, 207.0), contour=FACE_LOWER, mouth=(-2.0, 37.0, 8.0, 10.0, 1.8, -1.0), lip=(-1.0, 44.5, 5.5, -1.8))
        torso = B.region([(342, 301), (300, 310), (266, 322), (244, 340)],
                     [(244, 340), (246, 420), (244, 530)], ("L", [(244, 530), (536, 530)]),
                     [(536, 530), (538, 420), (536, 340)],
                     [(536, 340), (512, 322), (466, 308), (418, 300)], ("L", [(418, 300), (342, 301)]))
        sc.add("jer", K.fill(torso, K.RED) + K.outline(torso), torso)
        sc.part("hair", H.pageboy(**v["hair"]))
        if "far" in v:
            sc.part("hairF", H.pageboy(**v["far"]))
        sc.part("neck", K.neck(fc, bottom=312.0, width=40.0))
        sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
        sc.part("collar", B.falling_collar(**v.get("collar", {})))
        sc.part("ear", J.ear(fc))
        sc.part("cap", J.cap(fc, tip=(292.0, 171.0), top=(393.0, 106.0), flap_tip=(473.0, 130.0), hatband=10.5))
        return sc
    return b
run(sys.argv[1], [mk(v) for v in V], box=(300, 140, 520, 360), width=440)
