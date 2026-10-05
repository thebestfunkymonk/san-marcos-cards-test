"""Example: a card back — nested frames, a guilloché band, a Monarchs-style
step frame with fans, foil filigree corners and a guilloché medallion.
Built only from the public inkkit API (adapted from the toolkit review's
'piece 1'); writes out/back_design.{svg,png}, its print plates and a
preflight report.

    .venv/bin/python inkkit/examples/back_design.py
"""
import os
import sys
import time
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from inkkit import card, geom as G, ornament as O, preflight as PF, svg, tokens as T  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
INK, RED, FOIL, PAPER = T.INK, T.RED, T.FOIL, T.PAPER
W, Hh, cx, cy = card.W, card.H, card.CX, card.CY
FOIL_P = T.PRINT_PROFILES["foil"]


def main():
    t0 = time.time()
    doc = card.new_card(PAPER, layers=("paper", "red", "ink", "foil"), title="back design")
    doc.add_def(svg.foil_gradient("foil", FOIL))
    doc.layer_style("foil", fill="url(#foil)")
    fill = lambda d, c=INK: svg.path(d, fill=c)
    strk = lambda d, w=1.05, c=INK: svg.path(d, fill="none", stroke=c, stroke_width=w, stroke_linecap="round")

    # nested frame system
    doc.add(fill(O.rules(24, 24, W - 48, Hh - 48, [(0, 3.0), (5.5, 1.2)], r=18)), layer="ink")
    gb = O.guilloche_frame(36, 36, W - 72, Hh - 72, 12, width=14, wavelength=14, lines=8, amps=(1, 0.55),
                           auto_lines=True)
    doc.add(strk(gb), layer="ink")
    doc.add(fill(O.rope(O.frame_path(54, 54, W - 108, Hh - 108, 10, "round", 0), 7, 5, style="line",
                        lw=1.05)), layer="ink")
    doc.add(fill(O.rules(66, 66, W - 132, Hh - 132, [(0, 1.6), (5, 1.1)], r=34, corner="step2")), layer="ink")
    # a band laid out side by side, with pearl blocks at the corners
    doc.add(fill(O.frame_strip(88, 88, W - 176, Hh - 176, "band", 12, fill="triangles", lw=1.05,
                               corner="pearl")), layer="ink")
    # Monarchs-style fans in the step corners
    for (x, y, a0, a1) in ((66, 66, 0, 90), (W - 66, 66, 90, 180), (66, Hh - 66, 270, 360),
                           (W - 66, Hh - 66, 180, 270)):
        doc.add(fill(O.fan(x + (8 if a0 in (0, 270) else -8), y + (8 if a0 in (0, 90) else -8), 26, a0, a1, 7,
                           rims=(1, 0.75), hub=6, lw=1.05)), layer="ink")

    # foil filigree corners at foil-safe weights
    doc.add(fill(O.filigree_corners((116, 116, W - 232, Hh - 232), 150, 3, min_width=FOIL_P["min_line"],
                                    gap=FOIL_P["min_gap"], width=5.2), None), layer="foil")

    # medallion: rosette ring + fitted spirograph rosette + compass star
    r_out = 150
    doc.add(fill(O.rules(cx - r_out - 8, cy - r_out - 8, 2 * r_out + 16, 2 * r_out + 16, [(0, 2.0), (4, 1.1)],
                         r=r_out + 8)), layer="ink")
    doc.add(strk(O.rosette_ring(cx, cy, 72, r_out, bands=3, lobes=(18, 30, 42), lines=10, phase_span=1.0,
                                shape=0.9, auto_lines=True)), layer="ink")
    R, r, d = O.spirograph_fit(36, 66, petals=16, loops=7)
    doc.add(strk(O.spiro_rosette(cx, cy, R, r, d, copies=3), 1.05, RED), layer="red")
    doc.add(fill(G.outline(G.circle_d(cx, cy, 68), 1.4)), layer="ink")
    star = O.starburst(cx, cy, 30, 9, 8, layers=2, lw=FOIL_P["min_line"])
    doc.add(fill(G.offset(star, 3), PAPER), layer="red", knockout=True)   # clear the red under the star
    doc.add(fill(star, None), layer="foil")
    doc.add(fill(O.sunburst(cx, cy, r_out + 14, r_out + 40, 96, style="line", lw=1.2)), layer="ink")

    os.makedirs(OUT, exist_ok=True)
    fn = doc.save(os.path.join(OUT, "back_design.svg"))
    card.render(fn, fn[:-4] + ".png", 1500)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        doc.save_layers(os.path.join(OUT, "back_design-plate"))
    rep = PF.preflight(doc, profiles={"foil": "foil"}, overlay=os.path.join(OUT, "back_design-preflight"))
    print(PF.summary(rep))
    print(f"built in {time.time() - t0:.1f}s, {os.path.getsize(fn) // 1024} KB -> {fn}")


if __name__ == "__main__":
    main()
