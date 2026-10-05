
import sys
sys.path.insert(0, "work/ac-followup")
import reed_w as RW
from art import AC as _AC
from art import _aces_common as A
from deck import tokens as T
from deck.cardsvg import layers_merge
KW = dict(n_pairs=3, outer=dict(L=96.0, ratio=13.5, angle=12.0, bend=(-6.0, 14.0)), inner=dict(L=56.0, ratio=13.0, angle=28.0, bend=(-6.0, 12.0)))
def build():
    pip = A.knocked_pip("C", _AC.spray(), color=T.INK)
    wr = A.behind(RW.wreath(_AC.CX, A.CY, KW.pop("r", 190.0), **KW), "C")
    gold = A.keyline("C") + wr + A.caption("C")
    return layers_merge((pip + gold).fragments())
