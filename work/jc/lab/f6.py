import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_face as F, _jc_parts as J, _jc_head as H, _jc_body as B
FACE_LOWER = [(429, 207), (427, 234), (418, 256), (398, 273), (377, 280), (362, 275), (351, 259), (345, 234), (341, 207)]
V = json.loads(sys.argv[2])
def mk(v):
    def b():
        sc = K.Scene(rank="J")
        kw = dict(contour=FACE_LOWER, mouth=(-2.0, 37.0, 8.0, 10.0, 1.8, -1.0), lip=(-1.0, 44.5, 5.5, -1.8))
        kw.update({k: (tuple(tuple(x) if isinstance(x, list) else x for x in val) if isinstance(val, list) else val) for k, val in v.items()})
        fc = F.face_jc((385.0, 207.0), **kw)
        torso = B.region([(342, 301), (300, 310), (266, 322), (244, 340)],
                     [(244, 340), (246, 420), (244, 530)], ("L", [(244, 530), (536, 530)]),
                     [(536, 530), (538, 420), (536, 340)],
                     [(536, 340), (512, 322), (466, 308), (418, 300)], ("L", [(418, 300), (342, 301)]))
        sc.add("jer", K.fill(torso, K.RED) + K.outline(torso), torso)
        sc.part("hair", H.pageboy(outer=[[446,170],[470,194],[480,228],[478,266],[470,296],[452,316]], inner=[[420,320],[396,300],[392,262],[398,226],[412,190],[430,172],[446,170]], n=4, ends=[168,148,128,108], curl_deg=120))
        sc.part("neck", K.neck(fc, bottom=312.0, width=40.0))
        sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
        sc.part("collar", B.falling_collar(cf=[369,300], L0=[348,290], Lo=[318,316], Lt=[346,340], R0=[408,288], Ro=[438,308], Rt=[394,342], ci_dy=10, hem=7.0))
        sc.part("ear", J.ear(fc))
        sc.part("cap", J.cap(fc, tip=(292.0, 171.0), top=(393.0, 106.0), flap_tip=(473.0, 130.0), hatband=10.5))
        print("strokes", fc.strokes)
        return sc
    return b
run(sys.argv[1], [mk(v) for v in V], box=(320, 170, 450, 300), width=390)
