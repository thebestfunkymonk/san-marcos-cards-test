
import sys
sys.path.insert(0, "work/ac-followup")
import reed_w as RW
from art import AC as _AC
from art import _aces_common as A
from deck import tokens as T
from deck.cardsvg import layers_merge
KW = dict()
def build():
    pip = A.knocked_pip("C", _AC.spray(), color=T.INK)
    wr = A.behind(RW.wreath(_AC.CX, A.CY, KW.pop("r", 190.0), **KW), "C")
    gold = A.keyline("C") + wr + A.caption("C")
    return layers_merge((pip + gold).fragments())
