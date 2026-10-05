import os, sys
GEO = "/home/luke/Projects/design/san-marcos-deck/work/ks-panel/geo"
sys.path.insert(0, GEO)
import kit as K
import face as FC
from deck.motifs import core as C
def build():
    f = C.Frag()
    for cx, turn in ((240, 0), (375, -1), (510, 1)):
        s = FC.FaceSpec(cx=cx, head_cy=300, eye_y=307, brow_y=294, nose_top=302, nose_bot=334,
                        mouth_y=355, lip_y=362, turn=turn)
        fc = FC.face(s)
        f += fc.lines + K.outline(fc.head)
    f += K.fill(K.box(150, 450, 600, 505) if hasattr(K,'box') and isinstance(K.box(150,450,600,505), str) else "M150 450H600V505H150Z", "#1D5A55")
    f += K.fill("M150 60H160V70H150Z", "#AE2F2B") + K.fill("M590 60H600V70H590Z", "#B08D57")
    return f.layers()
