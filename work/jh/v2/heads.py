import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jh/v2")
from lib import render, OUT
import subprocess
from art import _jh_face as JF
from deck import courtkit as K
X, Y = 392.0, 206.0
variants = [dict(), dict(nose_len=8.4, lid_sag=3.8), dict(front_drop=2.6, lid_sag=2.6, pupil_tuck=1.6)]
tiles = []
for i, v in enumerate(variants):
    sc = K.Scene()
    fc = JF.minstrel_profile((X, Y), **v)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    f = sc.compose()
    print(i, fc.strokes, [(e['action'], e['role'], e.get('near')) for e in sc.heal_log])
    tiles.append(render([f], (X - 70, Y - 50, X + 60, Y + 110), f"head{i}", 390))
subprocess.run(["magick", *tiles, "+append", OUT + "/heads.png"])
