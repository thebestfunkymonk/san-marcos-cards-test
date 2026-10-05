import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/ks-panel/geo")
import kit as K
from deck import tokens as T
from deck.motifs import lion as L
from deck.motifs import core as C
def build():
    f = K.fill(K.D(K.box(250,300,500,450)), T.RED)
    f += K.fill(K.D(K.box(150,460,600,505)), T.JADE)
    f += K.fill(K.D(K.box(590,60,600,70)), T.FOIL)
    f += L.lion_mark(320, 375, 40, style="solid")
    f += L.lion_mark(430, 375, 60, style="solid")
    return C.frag(f).layers()
