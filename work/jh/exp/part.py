import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jh/exp")
from render import render
from art import _jh_parts as JP
from deck import courtkit as K
def show(parts, box, name, w=600):
    sc = K.Scene()
    for i, p in enumerate(parts):
        sc.part(f"p{i}", p)
    f = sc.compose()
    render([f], box, f"/home/luke/Projects/design/san-marcos-deck/work/jh/exp/{name}.png", w)
    return sc
