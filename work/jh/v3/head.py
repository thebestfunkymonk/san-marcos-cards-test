"""Head experiments: python work/jh/v3/head.py -> work/jh/v3/out/heads.png"""
import sys, subprocess, importlib
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
sys.path.insert(0, ROOT + "/work/jh/v2")
from lib import render
import lib
lib.OUT = ROOT + "/work/jh/v3/out"
from deck import courtkit as K
from art import _jh_face as JF, _jh_parts as JP, _jh_head as JHd

HEAD = (392.0, 206.0)


def head_scene(v):
    sc = K.Scene()
    fc = JF.minstrel_profile(HEAD, **v.get("face", {}))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("collar", JP.collar((368, 280), (424, 275), (366, 302), (428, 297), bot_sag=4.0))
    b = v.get("bob")
    if b:
        sc.part("hair", JHd.bob(b["outline"], b["guide"], n=b.get("n", 4), filler=fc.skin.intersection(K.box(*b["fill_box"])) if b.get("fill_box") else None,
                                stagger=b.get("stagger", 7.0), curl_deg=b.get("curl_deg", 110.0)))
    pl = v.get("plume")
    if pl and not v.get("plume_front"):
        sc.part("plume", JHd.plume(pl["guide"], **pl.get("kw", {})))
    bt = v["beret"]
    sc.part("beret", JHd.soft_beret(bt["disc"], bt["band_lo"], bt.get("band_h", 13.0), fc.skin, **bt.get("kw", {})))
    if pl and v.get("plume_front"):
        if pl.get("locks"):
            sc.part("plume", JP.plume_locks(pl["guide"], **pl.get("kw", {})))
        else:
            sc.part("plume", JHd.plume(pl["guide"], **pl.get("kw", {})))
    br = v.get("brooch")
    if br:
        sc.part("brooch", JP.fluke_heart(br, u=21.0, bezel=3.4))
    return sc



BOB = dict(outline=[(412, 192), (440, 192), (452, 214), (456, 246), (452, 268), (432, 274), (418, 262), (414, 232)],
           guide=[(426, 186), (442, 206), (446, 238), (440, 266)], fill_box=(380, 150, 470, 199))
DISC_A = [(334, 172), (352, 146), (398, 125), (450, 115), (490, 122), (506, 142), (494, 163), (462, 177), (410, 178), (356, 178)]
DISC_B = [(330, 174), (344, 150), (392, 128), (448, 118), (494, 124), (512, 146), (500, 168), (470, 182), (410, 180), (352, 180)]

from art._jh_parts import disc_pts
BAND = ((358, 183), (442, 196))
def B(c, rx, rt, rb, tilt, **kw):
    return dict(disc=disc_pts(c, rx, rt, rb, tilt), band_lo=BAND, band_h=13.0, kw=kw)

BOB2 = dict(outline=[(416, 196), (452, 194), (462, 218), (462, 250), (454, 272), (432, 276), (420, 262), (418, 238)],
           guide=[(430, 190), (446, 210), (450, 240), (444, 268)], fill_box=(380, 150, 470, 199))
D0 = [(340, 177), (356, 150), (400, 128), (452, 119), (494, 130), (512, 156), (508, 188), (488, 200), (462, 190), (410, 180), (356, 182)]
D1 = [(336, 176), (350, 152), (394, 130), (450, 116), (498, 124), (520, 150), (516, 184), (494, 198), (470, 188), (410, 180), (352, 182)]
D2 = [(342, 178), (360, 150), (406, 130), (458, 122), (500, 134), (516, 162), (506, 196), (484, 204), (464, 190), (410, 181), (356, 183)]

BOB3 = dict(outline=[(419, 194), (452, 194), (464, 218), (464, 250), (456, 272), (434, 277), (421, 262), (419, 236)],
           guide=[(432, 190), (448, 210), (452, 240), (446, 268)], fill_box=(380, 150, 470, 199))
PL = [(404, 160), (446, 120), (496, 82), (548, 66), (584, 84)]

PL = [(404, 160), (440, 118), (488, 80), (540, 62), (576, 70), (592, 94)]
PLK = dict(n=4, ends=(1.0, 0.92, 0.84, 0.76), tip_curl=(11.0, 240.0), curl_deg=110.0, smooth=10.0)
V0 = dict(
    beret=dict(disc=D1, band_lo=BAND, band_h=16.0, kw=dict(bead_d=6.3)),
    brooch=(404, 160),
    plume=dict(guide=PL, locks=True, kw=PLK),
    bob=BOB3, plume_front=True,
)
V1 = dict(V0, brooch=(410, 158), plume=dict(guide=[(410, 158), (444, 116), (490, 82), (540, 66), (574, 74), (590, 98)], locks=True, kw=dict(PLK, n=3, ends=(1.0, 0.9, 0.8))))
V2 = dict(V0, brooch=(398, 162), plume=dict(guide=[(398, 162), (436, 124), (484, 94), (536, 80), (574, 88), (592, 112)], locks=True, kw=dict(PLK, tip_curl=(12.0, 250.0))))
variants = [V0, V1, V2]
tiles = []
for i, v in enumerate(variants):
    sc = head_scene(v)
    f = sc.compose()
    roles = {}
    for e in sc.heal_log:
        roles[(e['action'], e['role'])] = roles.get((e['action'], e['role']), 0) + 1
    print(i, roles)
    tiles.append(render([f], (300, 50, 611, 330), f"head{i}", 600))
subprocess.run(["magick", *tiles, "+append", lib.OUT + "/heads.png"])
