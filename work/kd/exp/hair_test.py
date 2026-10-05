import sys; sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
from deck import courtkit as K
from art import _kd_head as H, _kd_crown as CR
SPECS = [K.HairSpec(top=(-50.0, -28.0), bulge=(-80.0, 32.0), bottom=(-50.0, 94.0), ribbons=6, over=14.0),
         K.HairSpec(top=(-48.0, -26.0), bulge=(-78.0, 40.0), bottom=(-40.0, 88.0), ribbons=5, over=14.0)]
import os
IDX = int(os.environ.get("HIDX", "0"))
def figure():
    sc = K.Scene(rank="K")
    fc = K.face((385.0, 207.0), "profile-left", age="elder", lids="heavy")
    fc.lines = fc.lines.select(lambda m: m.role not in ("jaw",))
    skin = fc.skin.intersection(K.box(0.0, 0.0, 750.0, 321.0))
    sc.part("hair", K.hair_fall(fc, +1, SPECS[IDX]))
    sc.add("head", fc.lines + K.outline(skin), skin)
    mo = H.profile_moustache(fc)
    sc.part("beard", H.squared_beard(fc, mo=mo))
    sc.part("moustache", mo)
    sc.part("crown", CR.dome_crown())
    return sc
def build():
    return figure().layers()
