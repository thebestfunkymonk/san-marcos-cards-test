
from art import AC as _AC
from art import _aces_common as A
from art import _aces_reed as R
from deck import tokens as T
from deck.cardsvg import layers_merge
KW = dict(leaf_len=84.0, width=6.6, ratio=13.0, angle=18.0, bend=(20.0,-24.0), inner_scale=0.62, inner_angle=30.0)
def build():
    pip = A.knocked_pip("C", _AC.spray(), color=T.INK)
    wr = A.behind(R.wreath(_AC.CX, A.CY, 190.0, spike=None, **KW), "C")
    gold = A.keyline("C") + wr + A.caption("C")
    return layers_merge((pip + gold).fragments())
