import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sketch import render, ROOT
from deck import courtkit as K
import _jc_face as F
import _jc_parts as J
OUT = os.path.join(ROOT, "work/jc/out/sk2"); os.makedirs(OUT, exist_ok=True)
variants = [
    dict(),
    dict(lids="raised"),
    dict(brow_dy=-14.0, brow_sag=3.8, mouth_hw=8.5, bow_rise=1.0, bow_sag=-0.8),
    dict(lids="heavy", brow_dy=-13.0, brow_sag=3.0, mouth_hw=8.5, bow_rise=1.0, bow_sag=-0.8, near_pdx=-4.2, far_pdx=-2.4),
]
tiles = []
for i, v in enumerate(variants):
    sc = K.Scene()
    fc = F.face34((385.0, 207.0), **v)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("ear", J.ear(fc))
    p = os.path.join(OUT, f"face{i}.png")
    render([sc.compose()], (320, 150, 450, 290), p, 390)
    tiles.append(p)
    print(i, fc.strokes, [(e['role'], e['action'], e['at']) for e in sc.heal_log])
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, "faces.png")], check=True)
