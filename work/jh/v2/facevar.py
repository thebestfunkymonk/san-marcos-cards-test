import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jh/v2")
from lib import render, OUT
import subprocess
from art import _jh_face as JF
from deck import courtkit as K
from deck.motifs import core as C
X, Y = 392.0, 206.0
tiles = []
for i, v in enumerate([dict(), dict(mouth_len=10.5), dict(pupil_tuck=1.6, lid_sag=3.0, front_drop=2.4)]):
    fc = JF.minstrel_profile((X, Y), **v)
    sc = K.Scene(); sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    tiles.append(render([sc.compose()], (X - 60, Y - 30, X + 30, Y + 70), f"fv{i}", 360))
    print(i, [(e['action'], e['role']) for e in sc.heal_log])
subprocess.run(["magick", *tiles, "+append", OUT + "/facevar.png"])
