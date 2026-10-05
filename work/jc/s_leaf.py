import os, sys, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sketch import render, ROOT
from deck import courtkit as K
from deck.motifs import core as C
import _jc_body as B
OUT = os.path.join(ROOT, "work/jc/out/sk2")
tag = sys.argv[1]
V = json.loads(sys.argv[2])
tiles = []
for i, v in enumerate(V):
    f = B.pecan_leaf((14, 128), -58.0, **v)
    field = K.box(0, 0, 140, 140)
    red = K.fill(C.knockout(K.D(field), f), K.RED)
    p = os.path.join(OUT, f"{tag}{i}.png")
    render([red], (0, 0, 140, 140), p, 480)
    tiles.append(p)
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{tag}.png")], check=True)
