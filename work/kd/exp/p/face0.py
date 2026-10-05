import sys; sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
from deck import courtkit as K
def figure():
    sc = K.Scene()
    fc = K.face((388.0, 207.0), "profile-left", age="elder", lids="heavy", ears=True)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    print(fc.anchors['front'], fc.anchors['mouth_y'], fc.anchors['chin'], fc.anchors['ear'], fc.strokes)
    return sc
