import sys, subprocess
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/work/jh/v2")
from lib import render
import lib
lib.OUT = ROOT + "/work/jh/v3/out"
from deck import courtkit as K
from art import _jh_face as JF
import importlib
X, Y = 392.0, 206.0
variants = [dict(crease=7.0, brow_dy=-17.0, brow_sag=3.0), dict(crease=7.4, brow_dy=-17.5, lid_flick=2.5, nostril=(7.5, 0.6, -80.0, 3.4, 160.0)),
            dict(crease=7.4, brow_dy=-17.5, brow_sag=2.6, lid_sag=3.6, lid_flick=2.0, pupil_tuck=1.2, nostril=(7.5, 0.6, -80.0, 3.4, 160.0))]
tiles = []
for i, v in enumerate(variants):
    fc = JF.minstrel_profile((X, Y), **v)
    sc = K.Scene(); sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    f = sc.compose()
    print(i, fc.strokes, [(e['action'], e['role']) for e in sc.heal_log])
    tiles.append(render([f], (X - 55, Y - 30, X + 25, Y + 75), f"fv{i}", 400))
subprocess.run(["magick", *tiles, "+append", lib.OUT + "/faces.png"])
