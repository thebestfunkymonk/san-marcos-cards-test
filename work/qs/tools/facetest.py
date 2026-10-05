import sys, importlib
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qs/tools")
from r import render, montage
from deck import courtkit as K
import art._qs_face as QF
importlib.reload(QF)
variants = [
    dict(),
    dict(crease=True),
    dict(crease=True, lid_sag=4.2, crease_sag=3.6),
    dict(lid_sag=4.6, flick=5.5),
]
files = []
for i, v in enumerate(variants):
    fc = QF.oracle_face((386.0, 206.0), **v)
    f = K.fill(fc.skin, "#F4EFE3") + fc.lines + K.outline(fc.head, K.CONTOUR)
    files.append(render(f, f"/home/luke/Projects/design/san-marcos-deck/work/qs/p5/face{i}.png", (330, 150, 445, 285), 4))
    print(i, fc.strokes)
montage(files, "/home/luke/Projects/design/san-marcos-deck/work/qs/p5/faces.png", tile="4x1")
