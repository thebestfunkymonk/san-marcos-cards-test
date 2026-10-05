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
FV = dict(bow_rise=0.8, bow_sag=-0.5, chin_r=18.0, chin_dy=50.0, mouth_dy=40.0, lip_dy=47.5, brow_dy=-12.0, brow_sag=2.6, far_brow_sag=2.0, mouth_hw=9.5)
tiles = []
for i, v in enumerate(V):
    sc = K.Scene()
    fc = F.face34((385.0, 207.0), **FV)
    sc.part("hair", H.hair_locks(
        back=[(450, 166), (478, 184), (490, 214), (490, 248)],
        scallops=[(490, 248), (480, 268), (463, 280), (444, 284)],
        front=[(426, 274), (426, 220), (430, 176)],
        strand_guides=[[(472, 176), (482, 208), (482, 242), (478, 258)],
                       [(460, 184), (468, 218), (466, 254), (460, 270)],
                       [(447, 194), (452, 232), (447, 264), (440, 276)]],
        sag=9.0, curl_deg=120.0, curl_r=3.6))
    sc.part("neck", K.neck(fc, bottom=312.0, width=40.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("ear", J.ear(fc))
    capf = getattr(H, v.pop("fn", "")) if "fn" in v else J.cap
    sc.part("cap", capf(fc, **v))
    p = os.path.join(OUT, f"{tag}{i}.png")
    render([sc.compose()], (280, 80, 500, 300), p, 440)
    tiles.append(p)
    print(i, len(sc.heal_log), [e for e in sc.heal_log if e['action'] == 'UNRESOLVED'])
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{tag}.png")], check=True)
