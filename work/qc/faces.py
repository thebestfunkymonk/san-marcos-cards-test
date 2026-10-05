"""Face variant sheet: python work/qc/faces.py out.png  (variants defined below)"""
import sys, subprocess
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import courtkit as K, tokens as T
VARS = [
    dict(lids="heavy", pupil_dx=2.5, flick=3.0),
    dict(lids="heavy", pupil_dx=3.0, flick=4.0, mouth_hw=10.0, bow_rise=2.6, lip_hw=6.2, lip_dy=45.0),
    dict(lids="lowered", pupil_dx=3.0, flick=4.0, mouth_hw=10.0, bow_rise=2.6, lip_hw=6.2, lip_dy=45.0),
    dict(lids="level", pupil_dx=3.5, flick=4.0, mouth_hw=10.0, bow_rise=2.6, lip_hw=6.2, lip_dy=45.0, brow_sag=3.2),
    dict(lids="heavy", pupil_dx=3.0, flick=4.5, mouth_hw=10.5, bow_rise=2.8, lip_hw=6.5, lip_dy=45.5, brow_dy=-15.5,
         brow_sag=4.6, eye_w=25.0),
    dict(lids="half", pupil_dx=3.0, flick=4.0, mouth_hw=10.0, bow_rise=2.6, lip_hw=6.2, lip_dy=45.0),
]
import json
if len(sys.argv) > 2:
    VARS = json.loads(open(sys.argv[2]).read())
sc = K.Scene()
for i, v in enumerate(VARS):
    fc = K.face((80.0 + 130.0 * i, 120.0), "3/4-left", sex="f", **v)
    sc.add(f"h{i}", fc.lines + K.outline(fc.head), fc.skin)
    print(i, fc.strokes)
f = sc.compose(contour=0)
W = 130 * len(VARS) + 30
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 40 {W} 170" width="{W*4}" height="{170*4}">'
       f'<rect x="0" y="40" width="{W}" height="170" fill="{T.PAPER}"/>' + "".join(f.layers().get(L, "") for L in T.LAYERS) + "</svg>")
open(sys.argv[1].replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(W * 4), sys.argv[1].replace(".png", ".svg"), "-o", sys.argv[1]], check=True)
