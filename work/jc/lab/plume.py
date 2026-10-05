import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
from deck import frames as FR
import _jc_face as F, _jc_parts as J, _jc_head as H, _jc_paddle as PD, _jc_body as B
FACE_LOWER = [(429, 207), (427, 234), (418, 256), (398, 273), (377, 280), (362, 275), (351, 259), (345, 234), (341, 207)]
V = json.loads(sys.argv[2])
def mk(v):
    def b():
        sc = K.Scene(rank="J")
        fc = F.face_jc((385.0, 207.0), contour=FACE_LOWER, mouth=(-2.0, 37.0, 8.0, 10.0, 1.8, -1.0), lip=(-1.0, 44.5, 5.5, -1.8))
        sc.part("hair", H.pageboy(outer=[(446, 170), (470, 194), (480, 228), (477, 262), (463, 284), (440, 293)],
                              inner=[(396, 292), (392, 262), (398, 226), (412, 190), (430, 172), (446, 170)],
                              n=4, ends=[146.0, 126.0, 106.0, 88.0], curl_deg=120.0))
        sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
        sc.part("ear", J.ear(fc))
        for k, pl in enumerate(v["plumes"]):
            vane, quill = (H.heron_plume3 if pl.pop("v3", False) else H.heron_plume2)(**pl)
            sc.part(f"plume{k}", vane)
            sc.part(f"quill{k}", quill)
        sc.part("cap", J.cap(fc, tip=(292.0, 171.0), top=(393.0, 106.0), flap_tip=(473.0, 130.0), hatband=10.5))
        sc.part("paddle", PD.paddle3(548.0, **v.get("paddle", dict(square=18, hw=30, widest=175, shoulder=246, band=(204, 224), taper=0.55))))
        return sc
    return b
tiles = []
for i, v in enumerate(V):
    sc = mk(v)()
    fr = K.C.stroke(FR.art_window_d(), K.FINE, color=K.GOLD)
    p = os.path.join(OUT, f"{sys.argv[1]}{i}.png")
    render([sc.compose(), fr], (280, 50, 615, 300), p, 536)
    tiles.append(p)
    print(i, [(e['action'], e['role'], e['near']) for e in sc.heal_log if e['role'] in ('current','terminal','quill','outline')][:6])
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{sys.argv[1]}.png")], check=True)
