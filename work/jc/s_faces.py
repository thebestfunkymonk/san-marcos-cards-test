import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sketch import render, ROOT
from deck import courtkit as K
import _jc_parts as J
OUT = os.path.join(ROOT, "work/jc/out/sk"); os.makedirs(OUT, exist_ok=True)
variants0 = [
    dict(lids="level", pupil_dx=-3.5),
    dict(lids="raised", pupil_dx=-3.5),
    dict(lids="raised", pupil_dx=-4.0, brow_sag=4.2, brow_dy=-14.5, mouth_hw=10.0, lip_hw=6.5),
    dict(lids="level", pupil_dx=-4.0, brow_sag=2.2, brow_dy=-12.0, brow_drop=-1.0, mouth_hw=10.0, lip_hw=6.5, lip_dy=47.0),
]
variants = [
    dict(lids="level", pupil_dx=-4.0, flick=4.0),
    dict(lids="level", pupil_dx=-4.0, flick=4.0, brow_dy=-12.0, brow_out=31.0, brow_sag=3.8),
    dict(lids="heavy", pupil_dx=-4.0, flick=4.0, brow_dy=-12.0, brow_out=31.0, brow_sag=3.8, mouth_hw=10.0),
    dict(lids="level", pupil_dx=-4.0, flick=3.0, brow_dy=-12.5, brow_out=30.0, brow_sag=2.6, brow_drop=0.5, mouth_hw=10.0, lip_hw=6.2),
]
tiles = []
for i, v in enumerate(variants):
    sc = K.Scene()
    fc = K.face((385.0, 207.0), "3/4-left", age="young", **v)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("ear", J.ear(fc))
    sc.part("cap", J.cap(fc))
    p = os.path.join(OUT, f"face{i}.png")
    render([sc.compose()], (320, 150, 450, 290), p, 390)
    tiles.append(p)
    print(i, fc.strokes, [e for e in sc.heal_log if e['role'] in ('lid','lid-lo','pupil','brow','nose','mouth','lip')])
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, "faces.png")], check=True)
