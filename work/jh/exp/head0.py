import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jh/exp")
from render import render
from deck import courtkit as K
X, Y = 385.0, 200.0
sc = K.Scene()
fc = K.face((X, Y), "profile-left", sex="m", age="young", lids="lowered", r=42.5)
sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
sc.part("hair", K.hair_back(fc, volume=9.0, n=4, nape_drop=24))
f = sc.compose()
print(fc.strokes, fc.anchors["front"], fc.anchors["eye"], fc.anchors["mouth_y"], fc.anchors["chin"], fc.anchors["neck_y"])
render([f], (X - 90, Y - 70, X + 90, Y + 120), "/home/luke/Projects/design/san-marcos-deck/work/jh/exp/head0.png", 540)
