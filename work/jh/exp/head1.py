import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jh/exp")
from render import render
from art import _jh_face
from deck import courtkit as K
X, Y = 390.0, 200.0
sc = K.Scene()
fc = _jh_face.profile_left((X, Y))
sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
f = sc.compose()
print(fc.strokes, sc.heal_log)
render([f], (X - 90, Y - 60, X + 70, Y + 120), "/home/luke/Projects/design/san-marcos-deck/work/jh/exp/head1.png", 480)
