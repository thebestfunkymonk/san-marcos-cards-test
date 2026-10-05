import sys, subprocess
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/work/jh/v2")
from lib import render
import lib
lib.OUT = ROOT + "/work/jh/v3/out"
from deck import courtkit as K
from art import _jh_parts as JP
FX = 530.0
vs = [dict(volute="spiral", scroll_r=21.5, pegbox_len=54.0, peg_t=(0.30, 0.50, 0.72, 0.92), peg_len=20.0, peg_aspect=0.66, waist=(35.0, 99.0), fhole=(25.0, 90.0, 28.0, 138.0, 3.6), bridge_ext=5.5),
      dict(volute="spiral", scroll_r=21.5, pegbox_len=54.0, peg_t=(0.30, 0.50, 0.72, 0.92), peg_len=20.0, peg_aspect=0.66, waist=(37.0, 100.0), fhole=(26.0, 92.0, 29.0, 140.0, 3.8), bridge_ext=5.0),
      dict(volute="spiral", scroll_r=21.5, pegbox_len=54.0, peg_t=(0.30, 0.50, 0.72, 0.92), peg_len=20.0, peg_aspect=0.66, waist=(35.0, 99.0), fhole=(24.0, 96.0, 28.5, 140.0, 3.2), bridge_ext=5.0)]
tiles = []
for i, v in enumerate(vs):
    sc = K.Scene()
    fd = JP.Fiddle(x=FX, body_top=296.0, **v)
    sc.part("fiddle-neck", fd.neck_part())
    K.fist((FX, 281.0), -90.0, shaft_w=18.0, back=+1, wrist=(552.0, 330.0), wrist_w=26.0, h=34.0).add_to(sc, "handR", halo=0.0)
    sc.part("fiddle-body", fd.body_part())
    f = sc.compose()
    print(i, [(e['action'], e['role']) for e in sc.heal_log])
    tiles.append(render([f], (470, 290, 590, 510), f"fd{i}", 400))
subprocess.run(["magick", *tiles, "+append", lib.OUT + "/fiddles.png"])
