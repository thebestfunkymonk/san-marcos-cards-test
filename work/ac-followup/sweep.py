"""vector QA-12 on the wreath for many KW variants (no raster):
python work/ac-followup/sweep.py 'KW1' 'KW2' ..."""
import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, "work/ac-followup")
import importlib
import reed_w as RW
from art import _aces_common as A
from deck import tokens as T, qa as Q
from deck import cardsvg as C
from deck.cardsvg import layers_merge

def run(kw):
    kw = dict(kw); r = kw.pop("r", 190.0)
    wr = A.behind(RW.wreath(375.0, A.CY, r, **kw), "C")
    gold = A.keyline("C") + wr
    doc = C.CardDoc("AC", stock="limestone", order=C.ACE_ORDER)
    doc.add_layers(layers_merge(gold.fragments()))
    vec = Q.vector_gaps(Q.card_geometry(doc.to_string()))
    return vec

if __name__ == "__main__":
    for s in sys.argv[1:]:
        vec = run(eval(s))
        print(len(vec), [(v["gap"], v["at"], v["rule"][:8]) for v in vec[:6]], "<-", s[:160])
