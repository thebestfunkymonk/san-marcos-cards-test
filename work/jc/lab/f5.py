import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_face as F
import _jc_parts as J
L1 = [(429,207),(426,236),(414,259),(395,274),(376,279),(361,273),(350,256),(345,232),(341,207)]
L2 = [(429,207),(427,234),(418,256),(398,273),(377,280),(362,275),(351,259),(345,234),(341,207)]
L3 = [(429,207),(426,238),(412,262),(390,278),(372,281),(359,273),(350,255),(344,230),(341,207)]
L4 = [(429,207),(428,230),(421,252),(403,270),(380,280),(364,277),(352,262),(345,236),(341,207)]
def mk(cont, **kw):
    def b():
        sc = K.Scene()
        fc = F.face_jc((385.0, 207.0), contour=cont, mouth=(-2.0, 37.0, 8.0, 10.0, 1.8, -1.0), lip=(-1.0, 44.5, 5.5, -1.8), **kw)
        sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
        sc.part("ear", J.ear(fc))
        sc.part("cap", J.cap(fc, tip=(292.0, 171.0), top=(393.0, 106.0), flap_tip=(473.0, 130.0), hatband=10.5))
        return sc
    return b
run("f5", [mk(L1), mk(L2), mk(L3), mk(L4)], box=(320, 170, 450, 300), width=390)
