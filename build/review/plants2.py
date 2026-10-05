import sys, os, types
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/build/review")
from harness import *
from harness import _load
from inkkit import geom as G, svg as S
from deck import frames as F, pips as P, tokens as T
import shapely

base = _load("KS").build()
def variant(extra):
    def b():
        from deck.cardsvg import layers_merge
        return layers_merge(base, extra)
    return types.SimpleNamespace(build=b)

# gold area for "15.3 % of the brief's art window (the drawable half, x139-611 y55-511)"
half = G.to_shape(G.intersection(F.art_window_d(), G.rect_d(0, 0, 750, 511)))
full = G.to_shape(F.art_window_d())
target = 0.153 * half.area
w = 400.0; h = target / w
gold_rect = G.rect_d(175, 180, w, h)
print(f"half window {half.area:.0f}  full window {full.area:.0f}  ratio {full.area/(2*half.area):.4f}  gold rect h {h:.2f}")

# 2.0 px knockout line through the red collar (§I.12 min 2.5)
collar = G.poly_d([(300, 300), (450, 300), (430, 350), (320, 350)], closed=True)
ko = G.outline(G.poly_d([(300, 325), (450, 325)]), 2.0, cap="butt", join="miter")
thin = G.outline(G.poly_d([(420, 200), (560, 200)]), 1.3, cap="butt", join="miter")
pip = F.corner_pip_d("S")
px0, py0, px1, py1 = G.bbox(pip)
V = {
 "A1-symbol-use-2.5": {"ink": ['<defs><symbol id="s1"><path d="M300 200l100 0" stroke="#15242B" stroke-width="2.5" fill="none"/></symbol></defs><use href="#s1" fill="none"/>']},
 "A2-nested-svg-x3": {"ink": ['<svg x="300" y="150" width="300" height="300" viewBox="0 0 100 100"><path d="M0 10l100 0" stroke="#15242B" stroke-width="2.1" fill="none"/></svg>']},
 "A3-css-transform": {"ink": ['<path d="M150 250l50 0" stroke="#15242B" stroke-width="2.1" fill="none" style="transform:scale(2)"/>']},
 "A4-parallel-gap3.4": {"ink": [S.path("M300 240l150 0M300 245.5l150 0", fill="none", stroke=T.INK, stroke_width=T.FINE)]},
 "A5-ko-line-2.0": {"red": [S.path(G.difference(collar, ko), fill=T.RED)]},
 "A6-fill-1.3": {"gold": [S.path(thin, fill=T.FOIL)]},
 "A7-gold-15.3pct-brief": {"gold": [S.path(gold_rect, fill=T.FOIL)]},
 "A8-art-11px-from-pip": {"gold": [S.path(G.circle_d(px1 + 11 + 5, (py0 + py1) / 2, 5), fill=T.FOIL)]},
 "A9-art-13px-from-pip": {"gold": [S.path(G.circle_d(px1 + 13 + 5, (py0 + py1) / 2, 5), fill=T.FOIL)]},
 "A10-gold-line-on-red": {"gold": [S.path("M330 310l0 30M345 310l0 30", fill="none", stroke=T.FOIL, stroke_width=T.FINE)]},
}
for name, extra in V.items():
    B.load_art = (lambda pid, e=extra: variant(e))
    a = B.build_piece("KS", "limestone"); wv = B.build_piece("KS", "white")
    if a.get("error"): print(a["error"])
    for rec in (a, wv):   # keep a copy for inspection
        import shutil; os.makedirs(os.path.join(REV, "plant"), exist_ok=True)
        shutil.copy(rec["svg"], os.path.join(REV, "plant", f"{name}{'' if rec is a else '-white'}.svg"))
    r = qa(a, wv)
    extra_s = f" gold%={r['5'].get('gold_pct')}" if "gold" in name else ""
    extra_s += f" min_clear={r['10c'].get('min_clear')}" if "pip" in name else ""
    print(f"{name:24}", summary(r), extra_s)
