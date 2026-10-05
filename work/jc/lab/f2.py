import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_face as F
import _jc_parts as J
import _jc_head as H
def mk(**kw):
    def b():
        sc = K.Scene()
        fc = F.face34((385.0, 207.0), **kw)
        sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
        sc.part("ear", J.ear(fc))
        sc.part("cap", J.cap(fc, tip=(292.0, 171.0), top=(393.0, 106.0), flap_tip=(473.0, 130.0), hatband=10.5))
        return sc
    return b
base = dict(bow_rise=0.8, bow_sag=-0.5, chin_r=18.0, chin_dy=50.0, mouth_dy=40.0, lip_dy=47.5,
            brow_dy=-12.0, brow_sag=2.6, far_brow_sag=2.0, mouth_hw=9.5)
v1 = dict(base, brow_dy=-10.5, brow_sag=4.5, far_brow_sag=3.5, lids="raised", flick=2.5)
v2 = dict(v1, lids="level", mouth_hw=10.5, bow_rise=2.0, bow_sag=-1.2, lip_dy=48.5, lip_hw=6.5)
v3 = dict(v2, chin_r=21.0, chin_dy=48.0, nose_tip=(-9.0, 17.0), hook=(3.8, 3.5))
v4 = dict(v3, lids="heavy", near_pdx=-3.5, far_pdx=-1.5)
run("f2", [mk(**base), mk(**v1), mk(**v2), mk(**v3), mk(**v4)], box=(320, 170, 450, 300), width=390)
