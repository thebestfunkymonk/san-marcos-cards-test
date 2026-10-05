import os, sys, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sketch import render, ROOT
from deck import courtkit as K
from deck import frames as FR
import _jc_face as F
import _jc_parts as J
import _jc_head as H
import _jc_paddle as PD
OUT = os.path.join(ROOT, "work/jc/out/sk2")
tag = sys.argv[1]
V = json.loads(sys.argv[2])
tiles = []
for i, v in enumerate(V):
    sc = K.Scene(rank="J")
    fc = F.face34((385.0, 207.0), bow_rise=0.8, bow_sag=-0.5)
    sc.part("hair", H.hair_locks(
        back=[(450, 166), (478, 184), (490, 214), (490, 248)],
        scallops=[(490, 248), (480, 268), (463, 280), (444, 284)],
        front=[(426, 274), (426, 220), (430, 176)],
        strand_guides=[[(472, 176), (482, 208), (482, 242), (478, 258)],
                       [(460, 184), (468, 218), (466, 254), (460, 270)],
                       [(447, 194), (452, 232), (447, 264), (440, 276)]],
        sag=9.0, curl_deg=120.0, curl_r=3.6))
    sc.part("neck", K.neck(fc, bottom=312.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("ear", J.ear(fc))
    vp, qp = H.heron_plume2(**v["plume"])
    sc.part("plume", vp); sc.part("quill", qp)
    sc.part("cap", J.cap(fc))
    sc.part("paddle", PD.paddle(548.0, **v.get("paddle", {})))
    p = os.path.join(OUT, f"{tag}{i}.png")
    fr = K.C.stroke(FR.art_window_d(), K.FINE, color=K.GOLD)
    render([sc.compose(), fr], (290, 50, 615, 300), p, 650)
    tiles.append(p)
    print(i, len(sc.heal_log), [e for e in sc.heal_log if e['action'] == 'UNRESOLVED'])
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{tag}.png")], check=True)
