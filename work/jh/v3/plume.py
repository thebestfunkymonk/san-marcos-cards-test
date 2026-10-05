import sys, subprocess
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/work/jh/v2")
from lib import render
import lib
lib.OUT = ROOT + "/work/jh/v3/out"
from deck import courtkit as K
from art import _jh_parts as JP
PL = [(404, 160), (440, 118), (488, 80), (540, 62), (576, 70), (592, 94)]
kws = [dict(n=4, ends=(1.0, 0.92, 0.84, 0.76), tip_curl=(10.0, 230.0), curl_deg=110.0, smooth=10.0, root_taper=90.0),
       dict(n=4, ends=(1.0, 0.93, 0.86, 0.79), tip_curl=(11.0, 250.0), curl_deg=120.0, smooth=12.0, root_taper=130.0),
       dict(n=5, ends=(1.0, 0.94, 0.88, 0.82, 0.76), tip_curl=(12.0, 250.0), curl_deg=120.0, smooth=12.0, root_taper=120.0)]
tiles = []
for i, kw in enumerate(kws):
    pt = JP.plume_locks(PL, **kw)
    sc = K.Scene(); sc.part("plume", pt)
    f = sc.compose()
    print(i, '  heal', [(e['action'], e['role']) for e in sc.heal_log])
    tiles.append(render([f], (390, 40, 611, 180), f"pl{i}", 500))
subprocess.run(["magick", *tiles, "+append", lib.OUT + "/plumes.png"])
