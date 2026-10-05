import sys; sys.path.insert(0,'.')
import numpy as np
from deck import qa as Q, tokens as T, frames as F
from inkkit import geom as G
svg = open(sys.argv[1]).read()
S = Q.SCALE; W3, H3 = T.W*S, T.H*S
order = list(T.LAYERS)
alpha = {L: Q._rsvg(Q._isolate(svg, L), W3)[..., 3] for L in T.LAYERS}
vis = {}; cover = np.zeros((H3, W3), np.float32)
for L in reversed(order):
    if L == 'paper': continue
    a = alpha[L].astype(np.float32)/255.0; vis[L] = a*(1-cover); cover = cover + vis[L]
halves = G.difference(F.art_window_d(), G.rect_d(0, F.BAND_Y0, T.W, F.BAND_Y1 - F.BAND_Y0))
win = Q._poly_mask(halves, (H3, W3), S); n = win.sum()
print({L: round(float(vis[L][win].sum()/n*100), 3) for L in vis})
