import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from render import render, ROOT
from deck import courtkit as K
from art import _qh_face as QF, _qh_head as QHd
OUT = os.path.join(os.path.dirname(__file__), "out"); os.makedirs(OUT, exist_ok=True)
cx, cy = 385.0, 203.0
fc = QF.queen_face((cx, cy), wing_mode="hook", wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)
def study(tag, poke=0.0, **kw):
    cap = QHd.Cap(fc, **kw)
    sc = K.Scene()
    sc.part("neck", K.neck(fc, bottom=330.0, width=30))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("capbody", cap.body())
    sc.part("rim", cap.rim())
    for j in range(cap.rows):
        sc.part(f"row{j}", cap.row(j, poke=poke))
    sc.part("pearl", QHd.pearl(cap.crown + K.P(0, -2), 20.0))
    f = sc.compose()
    print(tag, len(sc.heal_log), [e for e in sc.heal_log if e['action']=='UNRESOLVED'][:5])
    p = os.path.join(OUT, f"head-{tag}.png")
    render([f], (cx - 90, cy - 95, cx + 90, cy + 85), p, 540)
    return p
base = dict(step=16.0, length=20.0, pitch=26.0, front=(8.0, -33.0), far=(46.0, -12.0), near=(-47.0, 4.0))
tiles = [
  study("A", **base),
  study("B", poke=6.0, **base),
  study("C", poke=6.0, **{**base, "volume": 10.0, "pitch": 28.0}),
]
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, "heads.png")], check=True)
