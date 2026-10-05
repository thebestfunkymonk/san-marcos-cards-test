import os, sys, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sketch import render, ROOT
from deck import courtkit as K
import _jc_face as F
import _jc_parts as J
OUT = os.path.join(ROOT, "work/jc/out/sk2"); os.makedirs(OUT, exist_ok=True)
V = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [{}]
tag = sys.argv[2] if len(sys.argv) > 2 else "f"
box = (330, 180, 445, 275)
tiles = []
for i, v in enumerate(V):
    sc = K.Scene()
    fc = F.face34((385.0, 207.0), **v)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("ear", J.ear(fc))
    p = os.path.join(OUT, f"{tag}{i}.png")
    render([sc.compose()], box, p, 460)
    tiles.append(p)
    print(i, fc.strokes)
    for e in sc.heal_log:
        print("   ", e)
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{tag}.png")], check=True)
