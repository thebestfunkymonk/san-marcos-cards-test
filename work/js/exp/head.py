"""Head-only experiment for J♠."""
import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import courtkit as K
from art import _js_face as FACE, _js_hood as H
import importlib; importlib.reload(H); importlib.reload(FACE)

HEAD = (386.0, 208.0)

def figure():
    sc = K.Scene(rank="J")
    fc = FACE.page_profile(HEAD, +1, r=44.0)
    g = H.HoodGeo(fc)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("locks", H.locks(g))
    sc.part("hood", H.hood_part(g))
    sc.part("badge", K.lion_clasp((346.0, 190.0), 36.0))
    return sc

def build():
    return figure().layers()
