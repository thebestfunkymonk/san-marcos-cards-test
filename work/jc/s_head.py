import os, sys, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sketch import render, ROOT
from deck import courtkit as K
import _jc_face as F
import _jc_parts as J
import _jc_head as H
OUT = os.path.join(ROOT, "work/jc/out/sk2")
tag = sys.argv[1] if len(sys.argv) > 1 else "h"

def head(variant):
    sc = K.Scene()
    fc = F.face34((385.0, 207.0), bow_rise=0.8, bow_sag=-0.5)
    hf = K.HairSpec(top=(-40.0, -14.0), bulge=(-54.0, 34.0), bottom=(-46.0, 78.0), ribbons=3, over=4.0)
    sc.part("hair-far", K.hair_fall(fc, -1, hf))
    sc.part("hair", H.hair_bob(**variant["hair"]))
    sc.part("neck", K.neck(fc, bottom=310.0))
    sc.part("collar", J.collar(fc))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("ear", J.ear(fc))
    if variant.get("plume_behind"):
        sc.part("plume", H.heron_plume(**variant["plume"]))
        sc.part("cap", J.cap(fc))
    else:
        sc.part("cap", J.cap(fc))
        sc.part("plume", H.heron_plume(**variant["plume"]))
    return sc

V = [
 dict(hair=dict(outer=[(446, 176), (478, 196), (484, 236), (470, 276), (452, 294)],
                inner=[(420, 300), (425, 230), (430, 180)], n=4, side=-1),
      plume=dict(guide_pts=[(455, 160), (482, 150), (500, 172), (502, 214), (512, 250), (536, 262)], w_max=26)),
 dict(hair=dict(outer=[(446, 176), (478, 196), (484, 236), (470, 276), (452, 294)],
                inner=[(420, 300), (425, 230), (430, 180)], n=4, side=-1),
      plume=dict(guide_pts=[(456, 158), (474, 128), (478, 100), (496, 74), (524, 64)], w_max=24)),
 dict(hair=dict(outer=[(446, 176), (478, 196), (484, 236), (470, 276), (452, 294)],
                inner=[(420, 300), (425, 230), (430, 180)], n=4, side=-1),
      plume=dict(guide_pts=[(455, 160), (488, 146), (512, 150), (532, 140), (548, 118)], w_max=22)),
]
tiles = []
for i, v in enumerate(V):
    sc = head(v)
    p = os.path.join(OUT, f"{tag}{i}.png")
    render([sc.compose()], (280, 55, 611, 330), p, 660)
    tiles.append(p)
    bad = [e for e in sc.heal_log if e['action'] in ('UNRESOLVED',)]
    print(i, len(sc.heal_log), bad)
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{tag}.png")], check=True)
