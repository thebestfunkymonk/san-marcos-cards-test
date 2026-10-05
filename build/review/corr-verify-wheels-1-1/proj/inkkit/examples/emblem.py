"""Example: a heraldic emblem — tonal-engraved shield with a wavy river fess
and a foil star, a heraldic crown, a laurel + Texas wild-rice wreath, a
ripple-ring medallion and a ribbon with outlined type. Paper-filled shapes
act as knockouts in the print plates. Adapted from the toolkit review's
'piece 2'; writes out/emblem.{svg,png}, its plates and a preflight report.

    .venv/bin/python inkkit/examples/emblem.py
"""
import os
import sys
import time
import warnings

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from inkkit import card, geom as G, hatch as H, heraldry as HR, ornament as O  # noqa: E402
from inkkit import preflight as PF, svg, tokens as T  # noqa: E402
from inkkit.typeset import text_on_path  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
INK, RED, FOIL, PAPER = T.INK, T.RED, T.FOIL, T.PAPER
W, Hh = card.W, card.H
cx, cy = 375.0, 540.0
FOIL_P = T.PRINT_PROFILES["foil"]


def main():
    t0 = time.time()
    fill = lambda d, c=INK: svg.path(d, fill=c)
    doc = card.new_card(PAPER, layers=("paper", "ink", "red", "foil"), title="emblem")
    doc.add_def(svg.foil_gradient("foil", FOIL))
    doc.layer_style("foil", fill="url(#foil)")
    doc.add(fill(O.frame(24, 24, W - 48, Hh - 48, r=18, style="triple")), layer="ink")

    # ripple-ring medallion with a line sunburst behind the shield
    R_med = 250
    doc.add(fill(O.rules(cx - R_med, cy - R_med, 2 * R_med, 2 * R_med, [(0, 2.2), (5, 1.1)], r=R_med)), layer="ink")
    doc.add(fill(O.ripples(cx, cy, 206, count=6, spacing=6.4, growth=1.0, ry_ratio=1.0, width=2.0, breaks=5,
                           break_deg=14, fade=0.4)), layer="ink")
    doc.add(fill(O.rules(cx - 200, cy - 200, 400, 400, [(0, 1.3)], r=200)), layer="ink")
    doc.add(fill(O.beaded(G.circle_d(cx, cy, 194), 1.6, 2.8)), layer="ink")
    doc.add(fill(O.sunburst(cx, cy - 20, 60, 188, 72, style="line", lw=1.1, lengths=(1.0, 0.8))), layer="ink")

    # shield: paper halo (a knockout), tonal field, river fess, star, double outline
    sw, sh_ = 190, 230
    sx0, sy0 = cx - sw / 2, cy - 95
    shield = HR.shield(cx, sy0 + sh_ / 2, sw, sh_, "heater")
    doc.add(fill(G.offset(shield, 7), PAPER), layer="ink")
    tone = lambda x, y: np.clip(0.3 + 0.5 * ((x - sx0) / sw) ** 1.4 + 0.3 * ((y - sy0) / sh_) ** 2, 0, 1)
    field = H.tonal(shield, tone, angle=-35, spacing=4.2, wmin=0.6, wmax=2.4, fade=4, edge_gap=2.5, cross_at=0.7)
    top = f"M{sx0 - 5} {sy0 + 105} C {sx0 + 60} {sy0 + 85} {sx0 + 130} {sy0 + 125} {sx0 + sw + 5} {sy0 + 105}"
    bot = G.translate(top, 0, 34)
    band = G.intersection(G.poly_d(np.vstack([G.flatten(top)[0][0], G.flatten(bot)[0][0][::-1]]), True), shield)
    star = O.starburst(cx, sy0 + 55, 26, 10.5, 5, lw=FOIL_P["min_line"])
    field = G.knockout(field, band, 2.0)                          # geometric knockouts in the engraving
    field = G.knockout(field, O.starburst(cx, sy0 + 55, 26, 10.5, 5, facets=False), 3.5)
    doc.add(fill(field), layer="ink")
    doc.add(fill(H.between(top, bot, 6, clip=band, width=T.FINE, taper=4, min_width=1.05)), layer="ink")
    doc.add(fill(star, None), layer="foil")
    doc.add(fill(G.outline(shield, 3.2, join="miter")), layer="ink")
    doc.add(fill(G.outline(G.offset(shield, -5.5, join="miter"), 1.2, join="miter")), layer="ink")

    # crown on a paper halo
    crown = HR.crown(cx, sy0 - 12, 150, style="royal")
    doc.add(fill(G.offset(crown, 5), PAPER), fill(crown), layer="ink")

    # wreath: outlined, half-hatched laurel (left) and Texas wild rice (right)
    Rw = 168
    a = np.radians(np.linspace(100, 250, 200))
    left = np.column_stack([cx + Rw * np.cos(a), cy + 20 + Rw * np.sin(a)])
    doc.add(fill(O.laurel(left, count=11, leaf_len=34, leaf_w=13, stem_width=2.2, style="outline", lw=1.5,
                          hatch="half", berries=4, jitter=0.4)), layer="ink")
    right = G.mirror_x(G.poly_d(left), cx)
    doc.add(fill(O.rice(G.reverse(right), grains=16, grain_len=16, grain_w=4.4, awn=18, start=0.08, angle=28,
                        stem_width=2.4, pedicel=4)),
            layer="ink")

    # ribbon with type: silhouette knocks out what lies behind it
    rb = O.ribbon(cx - 150, cx + 150, cy + 205, 30, sag=-14, lw=1.6)
    doc.add(fill(rb["silhouette"], PAPER), fill(H.parallel(rb["back"], 45, 3.2, width=1.05)), fill(rb["lines"]),
            layer="ink")
    doc.add(fill(text_on_path("Cinzel", "SAN MARCOS", 17, rb["path"], variations={"wght": 700}, tracking=180),
                 RED), layer="red")

    os.makedirs(OUT, exist_ok=True)
    fn = doc.save(os.path.join(OUT, "emblem.svg"))
    card.render(fn, fn[:-4] + ".png", 1500)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        seps = doc.save_layers(os.path.join(OUT, "emblem-plate"))
    for f in seps:
        card.render(f, f[:-4] + ".png", 750, background="#FFFFFF")
    rep = PF.preflight(doc, profiles={"foil": "foil"}, overlay=os.path.join(OUT, "emblem-preflight"))
    print(PF.summary(rep))
    print(f"built in {time.time() - t0:.1f}s, {os.path.getsize(fn) // 1024} KB -> {fn}")


if __name__ == "__main__":
    main()
