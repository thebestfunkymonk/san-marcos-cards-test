import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jh/exp")
from render import render
import subprocess
from dataclasses import replace
from art import _jh_face as JF
from deck import courtkit as K
X, Y = 390.0, 200.0
variants = [dict(), dict(jaw_to=36, jaw_from=-4, jaw_sag=1.0), dict(front_drop=3.2, lid_sag=4.2, pupil_y=1.8)]
tiles = []
for i, v in enumerate(variants):
    sp = replace(JF.ProfileSpec(), **v)
    sc = K.Scene()
    fc = JF.profile_left((X, Y), sp)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    f = sc.compose()
    print(i, fc.strokes, [ (e['action'], e['role'], e['near']) for e in sc.heal_log])
    p = f"/home/luke/Projects/design/san-marcos-deck/work/jh/exp/hv{i}.png"
    render([f], (X - 70, Y - 30, X + 50, Y + 90), p, 360)
    tiles.append(p)
subprocess.run(["magick", *tiles, "+append", "/home/luke/Projects/design/san-marcos-deck/work/jh/exp/hv.png"])
