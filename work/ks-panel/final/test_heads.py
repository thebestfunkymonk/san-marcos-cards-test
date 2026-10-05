"""Kit generalisation test: three quick busts built ONLY from deck.courtkit
(+ deck.motifs), to show the kit draws other gazes, sexes and ages in the
K♠'s hand. Not cards — just enough of each figure to judge the head.

    .venv/bin/python work/ks-panel/final/test_heads.py   ->  work/ks-panel/final/out/test-heads.png (+ .svg, 3x crops)

  1  Q♠-style queen, 3/4 LEFT, closed lids with vestigial dots, stalactite
     diadem, gold hair in current lines, red gill-plume ruff, jade mantle,
     Lion Mark brooch.
  2  J♠-style page, strict PROFILE RIGHT, young, red hood with the Lion Mark
     badge, gold locks escaping, jade doublet.
  3  J♦-style herald, 3/4 RIGHT, young, flat red cap, short gold hair, red
     tabard with solid gold rowels, a fist on a diagonal trumpet.
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)

from deck import courtkit as K          # noqa: E402
from deck import tokens as T            # noqa: E402
from deck.motifs import fauna as MF     # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
X, Y = 375.0, 205.0                      # head centre (3/4 and profile heads sit at x ≈ 385)


def queen():
    sc = K.Scene()
    fc = K.face((X + 10, Y), "3/4-left", sex="f", age="adult", lids="closed", vestigial=True)
    hs = K.HairSpec(top=(-40.0, -30.0), bulge=(-56.0, 48.0), bottom=(-40.0, 124.0), ribbons=4, over=0.0)
    for side in (-1, 1):
        sc.part(f"hair{side}", K.hair_fall(fc, side, hs))
    # the ruff: a red standing collar BEHIND the mantle (its foot hides under the neckline)
    sc.part("ruff", K.standing_collar(X - 6, top_y=270.0, half_w=66.0, neck_y=284.0, shoulder=(-80.0, 306.0),
                                      color=K.RED, rim_color=K.JADE, rim=7.0, depth=60.0))
    sc.part("mantle", K.torso(X, neck_y=300.0, neck_hw=30.0, shoulder=(150.0, 356.0), side_x=160.0, turn=-1,
                              color=K.JADE, pattern_kind="karst", border=18.0, pitch=(26.0, 20.0)))
    sc.part("neck", K.neck(fc, bottom=330.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("hair-cap", K.hair_cap(fc, volume=9.0, hairline=0.55, n=3))
    # a coronet of graduated points standing on a band round the crown of the head
    # (a stalactite diadem hangs its points, and wants the plain ground of a veil)
    sc.part("diadem", K.diadem(y=Y - 32.0, h=9.0, bow=5.0, kind="point", n=3,
                               lengths=(24.0, 15.0), widths=(14.0, 11.0), fc=fc, jewel_r=0.0))
    sc.part("brooch", K.lion_clasp((X - 8.0, 376.0), 40.0))
    return sc, fc


def page():
    sc = K.Scene()
    fc = K.face((X + 10, Y), "profile-right", sex="m", age="young", lids="raised")
    sc.part("doublet", K.torso(X, neck_y=312.0, neck_hw=20.0, shoulder=(140.0, 350.0), side_x=150.0, turn=+1,
                               color=K.JADE, pattern_kind="bubbles", pitch=(30.0, 26.0), d=6.3))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("hood", K.cap(fc, kind="hood"))
    sc.part("badge", K.lion_clasp((X - 14.0, Y - 20.0), 40.0))
    return sc, fc


def herald():
    sc = K.Scene()
    fc = K.face((X + 10, Y), "3/4-right", sex="m", age="young", lids="level")
    sc.part("tabard", K.torso(X, neck_y=290.0, neck_hw=24.0, shoulder=(148.0, 352.0), side_x=150.0, turn=+1,
                              color=K.RED, pattern_kind="rowels_solid", pitch=(40.0, 36.0), r=8.5))
    sc.part("neck", K.neck(fc, bottom=312.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("hair", K.hair_cap(fc, volume=10.0, hairline=0.5, drop=16.0, n=3, parting=-12.0))
    sc.part("cap", K.cap(fc, kind="flat", rise=26.0, drop=0.50))
    tr = K.staff((440.0, 440.0), (575.0, 170.0), 14.0)
    sc.part("trumpet", tr, halo=K.HALO)
    K.fist((497.0, 326.0), -63.0, shaft_w=14.0, back=-1, wrist=(470.0, 372.0), h=34.0).add_to(sc, "hand")
    return sc, fc


def render(frags, box, path, width):
    x0, y0, x1, y1 = box
    parts = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{T.PAPER}"/>']
    for L in T.LAYERS:
        for f in frags:
            v = f.layers().get(L)
            if v:
                parts.append(v)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" width="{width}" '
           f'height="{int(width * (y1 - y0) / (x1 - x0))}">' + "".join(parts) + "</svg>")
    with open(path.replace(".png", ".svg"), "w") as fh:
        fh.write(svg)
    subprocess.run(["rsvg-convert", "-w", str(width), path.replace(".png", ".svg"), "-o", path], check=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    tiles = []
    for name, fn in (("queen-3q-left", queen), ("page-profile-right", page), ("herald-3q-right", herald)):
        sc, fc = fn()
        f = sc.compose()
        print(f"{name}: face strokes {fc.strokes}; heal changes {len(sc.heal_log)}")
        for e in sc.heal_log:
            if e["action"] == "UNRESOLVED" or e["role"] in ("lid", "lid-lo", "pupil", "brow", "nose", "mouth", "lip", "ear", "jaw"):
                print("   ", e)
        p = os.path.join(OUT, f"{name}.png")
        render([f], (215, 95, 575, 455), p, 720)
        render([f], (X - 80, Y - 70, X + 100, Y + 90), os.path.join(OUT, f"{name}-face3x.png"), 540)
        tiles.append(p)
    subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, "test-heads.png")], check=True)
    print(os.path.join(OUT, "test-heads.png"))


if __name__ == "__main__":
    main()
