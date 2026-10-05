import sys, os, re, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/build/review")
from harness import *
from inkkit import geom as G, svg as S
from deck import tokens as T, pips as P
man = {r["id"]: r for r in json.load(open(ROOT + "/build/manifest.json"))}
manw = {r["id"]: r for r in json.load(open(ROOT + "/build/white/manifest.json"))}
def with_d(old, new):
    return lambda t: t.replace(old, new, 1)
i3, w3 = man["3S"], manw["3S"]
t = open(i3["svg"]).read()
up = P.pip_d("S", 116, 375, 852, rotate=False); rot = P.pip_d("S", 116, 375, 852, rotate=True)
print("P9 mis-rotated bottom pip:", summary(plant(i3, w3, "P9-3S-bottom-pip-upright", with_d(rot, up))))
print("P9b pip moved 4 px:", summary(plant(i3, w3, "P9b-3S-pip-shift", with_d(rot, G.translate(rot, 4, 0)))))
tl = re.search(r'<path d="([^"]+)" fill="#15242B" class="index-rank" data-corner="tl"', t).group(1)
print("P10 index moved 2 px:", summary(plant(i3, w3, "P10-3S-index-2px", with_d(tl, G.translate(tl, 2, 0)))))
print("P10b index moved 0.9 px:", summary(plant(i3, w3, "P10b-3S-index-0.9px", with_d(tl, G.translate(tl, 0.9, 0)))))
print("P11 ink outside safe:", summary(plant(i3, w3, "P11-3S-safe", lambda s: s.replace('</g>\n</svg>', '<path d="M20 500h10v10h-10z" fill="#15242B" class="pip"/></g>\n</svg>'))))
print("P12 layer order:", summary(plant(i3, w3, "P12-3S-order", lambda s: s.replace('<g id="gold"', '<g id="goldX"'))))
print("P13 red on black card:", summary(plant(i3, w3, "P13-3S-red", lambda s: s.replace('</g>\n</svg>', '<path d="M300 500h10v10h-10z" fill="#AE2F2B"/></g>\n</svg>'))))
