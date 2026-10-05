import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from render import render, ROOT
from deck import courtkit as K
from art import _qh_face as QF, _qh_head as H
OUT = os.path.join(os.path.dirname(__file__), "out"); os.makedirs(OUT, exist_ok=True)
cx, cy = 380.0, 203.0
fc = QF.queen_face((cx, cy), wing_mode="hook", wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)
cap = H.Cap(fc, volume=13.0, step=18.0, length=22.0, pitch=30.0, front=(8.0, -33.0), far=(46.0, -12.0), near=(-48.0, 4.0))
hair = H.hair_stream([(336, 196), (300, 214), (268, 240), (262, 282), (276, 312)], 36.0, n=3, bubble_gap=1, side=+1)
print("hair lines", [(m.role, m.kind) for m in hair.lines.marks])
rows = [cap.row(j) for j in range(cap.rows)]
for j, r in enumerate(rows):
    print("row", j, len(r.meta["petals"]), r.shape.area)
# raw, no scene
render([cap.body().frag, cap.rim().frag] + [r.frag for r in rows] + [hair.frag], (cx - 130, cy - 90, cx + 90, cy + 130), os.path.join(OUT, "raw.png"), 660)
