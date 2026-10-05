import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jh/v2")
from lib import render, OUT
import subprocess
from shapely.geometry import Polygon
from art import _jh_parts as JP, _jh_face as JF
from deck import courtkit as K
fc = JF.minstrel_profile((392.0, 206.0))
filler = fc.skin.intersection(K.box(412, 150, 500, 262))
vs = [dict(guide=[(432, 176), (458, 188), (473, 216), (476, 250), (468, 280)], n=4, ends=(1.0, 0.94, 0.87, 0.80)),
      dict(guide=[(432, 176), (458, 188), (473, 216), (477, 250), (470, 282)], n=4, ends=(1.0, 0.92, 0.84, 0.76), curl_deg=(120,)),
      dict(guide=[(432, 176), (460, 188), (476, 216), (479, 250), (472, 284)], n=5, ends=(1.0, 0.95, 0.89, 0.83, 0.77), curl_deg=(110,))]
tiles = []
for i, v in enumerate(vs):
    g = v.pop("guide")
    p = JP.lock_bundle(g, filler=filler, **v)
    sc = K.Scene()
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("p", p)
    tiles.append(render([sc.compose()], (340, 160, 500, 320), f"hair{i}", 400))
subprocess.run(["magick", *tiles, "+append", OUT + "/hairs.png"])
