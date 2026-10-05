"""bal.py SVG... : unrounded §C.2 balance (as deck.qa check 5)."""
import sys, numpy as np
sys.path.insert(0, ".")
from deck import qa as QA, tokens as T, frames as F
from inkkit import geom as G
S = QA.SCALE
for svg in sys.argv[1:]:
    txt = open(svg).read()
    W3, H3 = T.W * S, T.H * S
    alpha = {L: QA._rsvg(QA._isolate(txt, L), W3)[..., 3] for L in T.LAYERS if L != "paper"}
    cover = np.zeros((H3, W3), np.float32); vis = {}
    for L in reversed(T.LAYERS):
        if L == "paper": continue
        a = alpha[L].astype(np.float32) / 255.0
        vis[L] = a * (1 - cover); cover += vis[L]
    halves = G.difference(F.art_window_d(), G.rect_d(0, F.BAND_Y0, T.W, F.BAND_Y1 - F.BAND_Y0))
    win = QA._poly_mask(halves, (H3, W3), S); n = win.sum()
    bal = {L: float(vis[L][win].sum() / n * 100) for L in vis}
    bal["paper"] = 100 - sum(bal.values())
    print(svg.split("/")[-2], " ".join(f"{k} {v:.2f}" for k, v in bal.items()))
