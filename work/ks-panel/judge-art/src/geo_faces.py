import os, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/ks-panel/geo")
import kit as K, face as FC
from deck import tokens as T
from deck.motifs import core as C
def build():
    sc = K.Scene()
    for cx, turn in ((240, 0), (375, -1), (510, 1)):
        fs = FC.FaceSpec(cx=cx, head_cy=300, eye_y=307, brow_y=294, nose_top=302, nose_bot=334, mouth_y=355, lip_y=362, turn=turn)
        f = FC.face(fs)
        sc.add(f"f{cx}", f.lines + K.outline(f.head), f.skin)
    sc.add("j", K.fill(K.D(K.box(150,450,600,505)), T.JADE), K.box(150,450,600,505))
    sc.add("r", K.fill(K.D(K.box(150,60,160,70)), T.RED), K.box(150,60,160,70))
    sc.add("g", K.fill(K.D(K.box(590,60,600,70)), T.FOIL), K.box(590,60,600,70))
    return sc.compose().layers()
