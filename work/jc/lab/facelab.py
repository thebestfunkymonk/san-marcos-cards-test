"""Face lab: render face variants (with cap + hair context) at 4x side by side.
usage: facelab.py tag  -- variants defined in VARIANTS below or via json argv[2]"""
import os, sys, json, subprocess
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "art")); sys.path.insert(0, os.path.join(ROOT, "work/jc"))
from sketch import render
from deck import courtkit as K
import importlib
OUT = os.path.join(ROOT, "work/jc/lab/out"); os.makedirs(OUT, exist_ok=True)

def run(tag, builders, box=(300, 140, 480, 320), width=540):
    tiles = []
    for i, b in enumerate(builders):
        sc = b()
        f = sc.compose()
        p = os.path.join(OUT, f"{tag}{i}.png")
        render([f], box, p, width)
        tiles.append(p)
        hl = [(e['action'], e['role'], e.get('near')) for e in sc.heal_log if e['role'] in ('pupil','lid','lid-lo','brow','nose','mouth','lip','ear','current','terminal')]
        print(i, hl[:8])
    subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{tag}.png")], check=True)
