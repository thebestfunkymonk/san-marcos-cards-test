"""Example: scrollwork at playing-card sizes — volutes from 60 to 120 px in
the engraved (taper) and monoline styles, pip-sized S/C scrolls, fleurons,
small filigree corners and bands. A quick visual check that curls keep
open eyes and every line prints (adapted from the toolkit review's
'stress_scroll'); writes out/scroll_study.{svg,png} and a preflight report.

    .venv/bin/python inkkit/examples/scroll_study.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from inkkit import card, geom as G, ornament as O, preflight as PF, stroke as S, svg, tokens as T  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def main():
    doc = svg.Doc(750, 560)
    doc.add(svg.rect(0, 0, 750, 560, fill=T.PAPER), layer="paper")
    f = lambda d: svg.path(d, fill=T.INK)
    x = 40
    for (L, w, tu) in [(60, 2.0, 1.25), (60, 3.0, 1.5), (80, 4.0, 1.75), (100, 5.0, 2.0), (120, 3.0, 2.25)]:
        doc.add(f(O.scroll((x, 60), 0, L, tu, width=w)), layer="ink")
        doc.add(f(O.scroll((x, 150), 0, L, tu, style="monoline", lw=T.FINE)), layer="ink")
        x += 140
    doc.add(f(O.s_scroll((60, 290), (160, 260), width=2.5)), layer="ink")
    doc.add(f(O.c_scroll((220, 280), (330, 280), width=2.5)), layer="ink")
    doc.add(f(O.scroll((380, 270), 0, 90, 1.25, width=4, leaves=2)), layer="ink")
    doc.add(f(O.fleuron(600, 280, 50, style="lily")), layer="ink")
    doc.add(f(O.fleuron(690, 280, 50, style="scroll")), layer="ink")
    doc.add(f(O.filigree_band(300, 24, x=180, y=390)), layer="ink")
    doc.add(f(O.filigree_corner(90, 3, x=420, y=350)), layer="ink")
    doc.add(f(O.filigree_corner(90, 1, x=560, y=350, style="monoline", lw=1.6)), layer="ink")
    for i, w in enumerate((1.0, 1.5, 2.0, 3.0)):
        pts = [(40 + i * 60, 540), (60 + i * 60, 490), (90 + i * 60, 510)]
        doc.add(f(S.stroke(G.smooth_d(pts), w, "taper-both", taper=0.35, min_width=T.MIN_LINE)), layer="ink")
    doc.add(f(S.stroke(G.circle_d(400, 510, 40), 8, "nib", nib_angle=40, nib_min=0.15)), layer="ink")
    doc.add(f(O.scroll((480, 500), 0, 160, 2.5, width=3)), layer="ink")
    doc.add(f(O.acanthus_leaf((650, 540), -60, 60, 22, lobes=3)), layer="ink")
    os.makedirs(OUT, exist_ok=True)
    fn = doc.save(os.path.join(OUT, "scroll_study.svg"))
    card.render(fn, fn[:-4] + ".png", 1500)
    print(PF.summary(PF.preflight(doc, overlay=os.path.join(OUT, "scroll_study-preflight"))))
    print("->", fn)


if __name__ == "__main__":
    main()
