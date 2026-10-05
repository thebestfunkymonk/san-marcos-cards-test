"""qbal.py [svg]: QA check 5's balance, unrounded (same masks as deck.qa)."""
import sys
sys.path.insert(0, '.')
import numpy as np
from deck import qa as Q, tokens as T, frames as F
from inkkit import geom as G
svg = open(sys.argv[1] if len(sys.argv) > 1 else 'cards/KH.svg').read()
S = Q.SCALE
W3, H3 = T.W * S, T.H * S
vis, cover = {}, np.zeros((H3, W3), np.float32)
for L in reversed(list(T.LAYERS)):
    if L == 'paper':
        continue
    a = Q._rsvg(Q._isolate(svg, L), W3)[..., 3].astype(np.float32) / 255.0
    vis[L] = a * (1.0 - cover)
    cover = cover + vis[L]
halves = G.difference(F.art_window_d(), G.rect_d(0, F.BAND_Y0, T.W, F.BAND_Y1 - F.BAND_Y0))
win = Q._poly_mask(halves, (H3, W3), S)
n = win.sum()
bal = {L: round(float(vis[L][win].sum() / n * 100), 3) for L in vis}
bal['paper'] = round(100 - sum(bal.values()), 3)
print(bal)
