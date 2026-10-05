import sys; sys.path.insert(0,'.')
import numpy as np
from deck import qa as Q, tokens as T, frames as F
from inkkit import geom as G
def bal(svg):
    s = open(svg).read()
    W3, H3 = int(T.W*Q.SCALE), int(T.H*Q.SCALE)
    alpha = {}
    for L in T.LAYERS:
        if L == 'paper': continue
        alpha[L] = Q._rsvg(Q._isolate(s, L), W3)[..., 3]
    vis = {}; cover = np.zeros((H3, W3), np.float32)
    for L in reversed(list(T.LAYERS)):
        if L == 'paper': continue
        a = alpha[L].astype(np.float32)/255.0
        vis[L] = a*(1-cover); cover = cover + vis[L]
    halves = G.difference(F.art_window_d(), G.rect_d(0, F.BAND_Y0, T.W, F.BAND_Y1 - F.BAND_Y0))
    win = Q._poly_mask(halves, (H3, W3), Q.SCALE)
    n = win.sum()
    b = {L: round(float(vis[L][win].sum()/n*100), 1) for L in vis}
    b['paper'] = round(100 - sum(b.values()), 1)
    return b
for p in sys.argv[1:]:
    b = bal(p)
    print(p.split('/')[-1], '  '.join(f"{k} {b[k]}" for k in ('paper','jade','red','gold','ink')))
