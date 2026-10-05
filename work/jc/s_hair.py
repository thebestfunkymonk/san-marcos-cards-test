import os, sys, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sketch import render, ROOT
from deck import courtkit as K
import _jc_face as F
import _jc_parts as J
import _jc_head as H
OUT = os.path.join(ROOT, "work/jc/out/sk2")
tag = sys.argv[1]
V = json.loads(sys.argv[2])
tiles = []
for i, v in enumerate(V):
    sc = K.Scene()
    fc = F.face34((385.0, 207.0), bow_rise=0.8, bow_sag=-0.5)
    if v.get("far"):
        sc.part("hair-far", K.hair_fall(fc, -1, K.HairSpec(**v["far"])))
    sc.part("hair", K.hair_fall(fc, +1, K.HairSpec(**v["near"])))
    sc.part("neck", K.neck(fc, bottom=310.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("ear", J.ear(fc))
    sc.part("cap", J.cap(fc))
    p = os.path.join(OUT, f"{tag}{i}.png")
    render([sc.compose()], (280, 90, 520, 330), p, 480)
    tiles.append(p)
    print(i, len(sc.heal_log), [e for e in sc.heal_log if e['action'] == 'UNRESOLVED'])
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{tag}.png")], check=True)
