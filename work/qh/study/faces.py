import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from render import render, ROOT
from deck import courtkit as K
OUT = os.path.join(os.path.dirname(__file__), "out"); os.makedirs(OUT, exist_ok=True)
C = (385.0, 203.0)
variants = {
  "half": dict(lids="half"),
  "half_flick": dict(lids="half", flick=3.0),
  "lowered": dict(lids="lowered"),
  "heavy": dict(lids="heavy"),
}
tiles = []
for name, kw in variants.items():
    fc = K.face(C, "3/4-right", sex="f", **kw)
    sc = K.Scene()
    sc.part("neck", K.neck(fc, bottom=330.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    f = sc.compose()
    p = os.path.join(OUT, f"face-{name}.png")
    render([f], (C[0]-70, C[1]-60, C[0]+80, C[1]+110), p, 450)
    tiles.append(p)
    print(name, fc.strokes, len(sc.heal_log))
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, "faces.png")], check=True)
