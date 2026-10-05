import sys, os, types, shutil
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/build/review")
from harness import *
from inkkit import geom as G, svg as S
from deck import frames as F, tokens as T
half = G.to_shape(G.intersection(F.art_window_d(), G.rect_d(0, 0, 750, 511)))
def run(name, layers, show=()):
    B.load_art = lambda pid: types.SimpleNamespace(build=lambda: layers)
    a = B.build_piece("KS", "limestone"); wv = B.build_piece("KS", "white")
    shutil.copy(a["svg"], os.path.join(REV, "plant", f"{name}.svg"))
    r = qa(a, wv)
    print(f"{name:26}", summary(r), " ".join(f"{k}={r[c].get(k)}" for c, k in show))
    return r
# A5: red panel with a 2.0 px knockout line (§I.12: knockout lines >= 2.5)
panel = G.rect_d(250, 300, 250, 80)
ko = G.outline(G.poly_d([(260, 340), (490, 340)]), 2.0, cap="butt", join="miter")
run("A5b-ko-line-2.0-isolated", {"red": [S.path(G.difference(panel, ko), fill=T.RED)],
                                 "ink": [S.path(panel, fill="none", stroke=T.INK, stroke_width=T.CONTOUR)],
                                 "jade": [S.path(G.rect_d(200, 400, 100, 60), fill=T.JADE)],
                                 "gold": [S.path(G.rect_d(420, 400, 60, 60), fill=T.FOIL)]})
# A7: ONLY gold, sized to 15.3 % of the brief's drawable-half window (minus medallion gold)
med_gold_top = 0.0
for pct in (15.3, 15.4):
    w = 400.0; h = pct / 100 * half.area / w
    run(f"A7b-gold-{pct}pct-of-half", {"gold": [S.path(G.rect_d(175, 180, w, h), fill=T.FOIL)],
                                       "ink": [S.path(G.rect_d(200, 440, 50, 30), fill=T.INK)],
                                       "red": [S.path(G.rect_d(300, 440, 50, 30), fill=T.RED)],
                                       "jade": [S.path(G.rect_d(400, 440, 50, 30), fill=T.JADE)]},
        show=(("5", "gold_pct"),))
# A8: art at 10 / 10.5 / 11 / 11.5 px from the corner pip (right edge of the pip bbox; spade widest at y ~ 118)
pip = F.corner_pip_d("S"); x0, y0, x1, y1 = G.bbox(pip)
import shapely
ps = G.to_shape(pip)
for gap in (10.0, 11.0, 11.5):
    c = G.circle_d(x1 + gap + 5, 118.0, 5)
    true = ps.distance(G.to_shape(c))
    run(f"A8b-pip-gap-{gap}", {"gold": [S.path(c, fill=T.FOIL)], "ink": [S.path(G.rect_d(200, 440, 50, 30), fill=T.INK)],
                              "red": [S.path(G.rect_d(300, 440, 50, 30), fill=T.RED)], "jade": [S.path(G.rect_d(400, 440, 50, 30), fill=T.JADE)]},
        show=(("10c", "min_clear"),))
    print("      true vector clearance", round(true, 2))
