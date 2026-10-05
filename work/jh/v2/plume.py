import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jh/v2")
from lib import render, OUT
import subprocess
from art import _jh_parts as JP
from deck import courtkit as K
G = [(404, 176), (420, 120), (458, 78), (512, 66), (548, 86), (556, 112)]
vs = [dict(), dict(n=5, ends=(1.0, 0.86, 0.73, 0.61, 0.49)), dict(n=4, ends=(1.0, 0.80, 0.62, 0.45), curl_deg=120)]
tiles = []
for i, v in enumerate(vs):
    p = JP.plume_locks(G, **v)
    sc = K.Scene(); sc.part("p", p)
    tiles.append(render([sc.compose()], (380, 40, 600, 200), f"plume{i}", 440))
    print(i, [(e['action'], e['role']) for e in sc.heal_log])
subprocess.run(["magick", *tiles, "+append", OUT + "/plumes.png"])
