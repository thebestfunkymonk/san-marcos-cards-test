"""Kit sheet: renders the reusable pieces side by side so the next court can
start from them (run: .venv/bin/python work/ks-panel/illus/kit_sheet.py).

Row 1: frontal face (K♠ spec) · 3/4 left · 3/4 right · profile left · profile right
Row 2: fist (tips ±1) · cupping hand (±1) · orb · jewel · Lion Mark roundel
Writes out/kit_sheet.svg and out/kit_sheet.png (not a card; a working sheet).
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(HERE))))

from deck import tokens as T                      # noqa: E402
from deck.motifs import core as MC                # noqa: E402
from inkkit import geom as G                      # noqa: E402

import face as FK                                 # noqa: E402
import hands as HD                                # noqa: E402
import regalia as RG                              # noqa: E402
from scene import Scene, Part                     # noqa: E402


def cell(ox, oy):
    return ox, oy


def main():
    sc = Scene(outline_w=None)
    faces = [FK.frontal_face(100, 110), FK.three_quarter_face(260, 110, -1), FK.three_quarter_face(420, 110, +1),
             FK.profile_face(580, 110, -1), FK.profile_face(740, 110, +1)]
    for i, fc in enumerate(faces):
        sc.add(Part(f"face{i}", fc.sil, detail=fc.lines, clip_detail=False, contour=T.MEDIUM))
    y2 = 330
    for i, tips in enumerate((+1, -1)):
        x = 90 + i * 130
        sc.add(Part(f"shaft{i}", G.rect_d(x - 10.5, y2 - 70, 21, 140), fills=[(None, T.FOIL)], contour=T.MEDIUM))
        fs = HD.fist(x, y2, tips=tips)
        sc.add(Part(f"fist{i}", fs.mitten, detail=fs.lines, contour=T.MEDIUM))
        sc.add(Part(f"thumb{i}", fs.thumb, detail=fs.thumb_lines, contour=T.MEDIUM))
    for i, tips in enumerate((+1, -1)):
        x = 400 + i * 130
        ob = RG.orb(x, y2 - 10, 33)
        sc.add(Part(f"orb{i}", ob.sil, fills=ob.fills, detail=ob.lines))
        h = HD.cup(x, y2 - 10, 33, tips=tips)
        sc.add(Part(f"hand{i}", h.mitten, detail=h.lines, contour=T.MEDIUM))
        sc.add(Part(f"hthumb{i}", h.thumb, contour=T.MEDIUM))
    j = RG.jewel(680, y2, 12)
    sc.add(Part("jewel", j.sil, fills=j.fills, detail=j.lines, contour=T.MEDIUM))
    lm = RG.lion_roundel(760, y2, 18.2)
    sc.add(Part("lion", lm.sil, fills=lm.fills, detail=lm.lines, contour=T.MEDIUM))
    f = sc.compose()
    body = "".join(f'<g id="{k}">{v}</g>' for k, v in f.layers().items())
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 440" width="1680" height="880">'
           f'<rect width="840" height="440" fill="{T.PAPER}"/>{body}</svg>')
    out = os.path.join(HERE, "out")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "kit_sheet.svg"), "w").write(svg)
    subprocess.run(["rsvg-convert", os.path.join(out, "kit_sheet.svg"), "-o", os.path.join(out, "kit_sheet.png")],
                   check=True)
    print(os.path.join(out, "kit_sheet.png"))


if __name__ == "__main__":
    main()
