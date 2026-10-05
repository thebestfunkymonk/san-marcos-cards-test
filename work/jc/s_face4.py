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
    nk = v.pop("neck_w", None)
    fc = F.face34((385.0, 207.0), **v)
    sc.part("hair", H.hair_locks(
        back=[(450, 166), (478, 184), (490, 214), (490, 248)],
        scallops=[(490, 248), (480, 268), (463, 280), (444, 284)],
        front=[(426, 274), (426, 220), (430, 176)],
        strand_guides=[[(472, 176), (482, 208), (482, 242), (478, 258)],
                       [(460, 184), (468, 218), (466, 254), (460, 270)],
                       [(447, 194), (452, 232), (447, 264), (440, 276)]],
        sag=9.0, curl_deg=120.0, curl_r=3.6))
    sc.part("neck", K.neck(fc, bottom=312.0, width=nk))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("ear", J.ear(fc))
    sc.part("cap", J.cap(fc))
    p = os.path.join(OUT, f"{tag}{i}.png")
    render([sc.compose()], (300, 150, 470, 310), p, 510)
    tiles.append(p)
    print(i, fc.strokes, [(e['role'], e['near']) for e in sc.heal_log if e['role'] in ('pupil','lid','lid-lo','brow','nose','mouth','lip')])
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{tag}.png")], check=True)
