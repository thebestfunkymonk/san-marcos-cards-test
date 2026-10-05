import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_head as H, _jc_face as F, _jc_parts as J, _jc_body as B
FACE_LOWER = [(429, 207), (427, 234), (418, 256), (398, 273), (377, 280), (362, 275), (351, 259), (345, 234), (341, 207)]
def b():
    fc = F.face_jc((385.0, 207.0), contour=FACE_LOWER)
    sc = K.Scene()
    sc.part('hair', H.pageboy(outer=[[444,168],[470,192],[484,228],[482,264],[468,288],[446,299]], inner=[[412,294],[404,262],[404,226],[412,190],[430,172],[444,168]], n=4, ends=[165,130,104,84], curl_deg=120))
    sc.add('head', fc.lines + K.outline(fc.head), fc.skin)
    sc.part('ear', J.ear(fc))
    return sc
run("dbg", [b], box=(330, 150, 510, 330), width=540)
