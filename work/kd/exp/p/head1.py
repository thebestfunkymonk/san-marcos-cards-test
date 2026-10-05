import sys; sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
import importlib
from deck import courtkit as K
from art import _kd_head as H
from art import _kd_crown as CR
def figure():
    sc = K.Scene()
    fc = H.profile_face((388.0, 207.0))
    g = H.gold_mass(fc)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.add("ear", H.ear_marks(g), None)
    sc.part("hair", H.hair(fc, g))
    mo = H.profile_moustache(fc)
    sc.part("beard", H.beard(fc, g))
    sc.part("moustache", mo)
    sc.part("crown", CR.dome_crown())
    print("strokes", fc.strokes, "hair area", g['hair'].area, "beard", g['beard'].area)
    return sc
