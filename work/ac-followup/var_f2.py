
import sys
sys.path.insert(0, "work/ac-followup")
import reed_w as RW
from art import AC as _AC
from art import _aces_common as A
from deck import tokens as T
from deck.cardsvg import layers_merge
KW = dict(r=194.0, n_pairs=3, outer=dict(L=100.0, ratio=13.5, angle=10.0, bend=(-10.0, 14.0)), inner=dict(L=62.0, ratio=12.0, angle=26.0, bend=(-6.0, 14.0), split=0.3))
def build():
    pip = A.knocked_pip("C", _AC.spray(), color=T.INK)
    wr = A.behind(RW.wreath(_AC.CX, A.CY, KW.pop("r", 190.0), **KW), "C")
    gold = A.keyline("C") + wr + A.caption("C")
    return layers_merge((pip + gold).fragments())
