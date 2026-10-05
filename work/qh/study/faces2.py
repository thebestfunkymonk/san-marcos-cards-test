import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from render import render, ROOT
from deck import courtkit as K
from art import _qh_face as QF
OUT = os.path.join(os.path.dirname(__file__), "out"); os.makedirs(OUT, exist_ok=True)
C = (385.0, 203.0)
variants = {
  "a": dict(wing=(5.0, -2.0)),
  "h1": dict(wing_mode="hook", wing=(4.5, 75.0, 1.5)),
  "h2": dict(wing_mode="hook", wing=(3.5, 95.0, 2.5), lid_sag=3.6, low_sag=5.6),
  "h3": dict(wing_mode="hook", wing=(5.5, 60.0, 0.0), lid_sag=3.3, low_sag=5.8),
}
tiles = []
for name, kw in variants.items():
    fc = QF.queen_face(C, **kw)
    sc = K.Scene()
    sc.part("neck", K.neck(fc, bottom=330.0, width=30))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    f = sc.compose()
    p = os.path.join(OUT, f"qface-{name}.png")
    render([f], (C[0]-50, C[1]-30, C[0]+50, C[1]+70), p, 600)
    tiles.append(p)
    print(name, fc.strokes, sc.heal_log)
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, "qfaces.png")], check=True)
