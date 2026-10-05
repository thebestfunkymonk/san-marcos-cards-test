import os, sys, subprocess, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sketch import render, ROOT
from deck import courtkit as K
from shapely.geometry import Polygon
import _jc_face as F
import _jc_parts as J
import _jc_head as H
OUT = os.path.join(ROOT, "work/jc/out/sk2")
tag = sys.argv[1]
V = json.loads(sys.argv[2])

def bob(v):
    outer = [tuple(p) for p in v["outer"]]
    roll = [tuple(p) for p in v["roll"]]
    inner = [tuple(p) for p in v["inner"]]
    d_out = H.spl(outer + roll[1:])
    op = H.pts_of(d_out, 0.3)
    ip = H.pts_of(H.spl(inner), 0.3)
    reg = Polygon(np.vstack([op, ip])).buffer(0).buffer(1.0, join_style=1).buffer(-1.0, join_style=1)
    gp = H.pts_of(H.spl(outer + [v.get("ext", (outer[-1][0] - 6, outer[-1][1] + 40))]), 0.3)
    dists = [-(K.EDGE_CON + k * 7.0) for k in range(v.get("n", 4))]
    guides = H.offsets(gp, dists)
    ln = H.strands(guides, reg, curl_side=v.get("curl", -1), curl_r=v.get("r", 4.2), curl_deg=v.get("deg", 80))
    return K.Part(reg, K.fill(reg, K.GOLD), ln + K.outline(reg), {})

tiles = []
for i, v in enumerate(V):
    sc = K.Scene()
    fc = F.face34((385.0, 207.0), bow_rise=0.8, bow_sag=-0.5)
    if v.get("far"):
        sc.part("hair-far", K.hair_fall(fc, -1, K.HairSpec(**v["far"])))
    sc.part("hair", bob(v))
    sc.part("neck", K.neck(fc, bottom=310.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("ear", J.ear(fc))
    sc.part("cap", J.cap(fc))
    p = os.path.join(OUT, f"{tag}{i}.png")
    render([sc.compose()], (280, 90, 520, 330), p, 480)
    tiles.append(p)
    print(i, len(sc.heal_log), [e for e in sc.heal_log if e['action'] == 'UNRESOLVED'])
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{tag}.png")], check=True)
